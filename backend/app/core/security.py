"""
Security Module for CareFlow AI

Handles JWT tokens, password hashing, and PHI encryption.
Compliant with HIPAA/GDPR security requirements.
"""

import hashlib
import hmac
import secrets
from base64 import urlsafe_b64encode, urlsafe_b64decode
from datetime import datetime, timedelta
from typing import Any, Dict, Literal, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# =============================================================================
# Password Hashing
# =============================================================================
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.

    Args:
        password: The plain text password to hash

    Returns:
        The hashed password
    """
    return pwd_context.hash(password)


def validate_password_strength(password: str) -> tuple[bool, list[str]]:
    """
    Validate password meets strength requirements.

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    if len(password) < settings.password_min_length:
        errors.append(f"Password must be at least {settings.password_min_length} characters")

    if settings.password_require_uppercase and not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if settings.password_require_lowercase and not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if settings.password_require_digit and not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    if settings.password_require_special:
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            errors.append("Password must contain at least one special character")

    return len(errors) == 0, errors


# =============================================================================
# JWT Tokens
# =============================================================================
def create_access_token(
    subject: str | Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Create a JWT access token.

    Args:
        subject: Subject identifier (usually user ID)
        expires_delta: Optional custom expiration time
        additional_claims: Additional claims to include in token

    Returns:
        Encoded JWT token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.jwt_access_token_expire_minutes
        )

    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "access",
    }

    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def create_refresh_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a JWT refresh token.

    Args:
        subject: Subject identifier (usually user ID)
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT refresh token
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )

    to_encode = {
        "exp": expire,
        "iat": datetime.utcnow(),
        "sub": str(subject),
        "type": "refresh",
        "jti": secrets.token_urlsafe(16),  # Unique token ID for revocation
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.secret_key_refresh,
        algorithm=settings.jwt_algorithm,
    )
    return encoded_jwt


def decode_token(token: str, secret: Optional[str] = None) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: The JWT token to decode
        secret: Optional secret key (defaults to access token secret)

    Returns:
        Decoded token payload

    Raises:
        JWTError: If token is invalid or expired
    """
    if secret is None:
        secret = settings.secret_key

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=[settings.jwt_algorithm],
        )
        return payload
    except JWTError as e:
        raise JWTError(f"Invalid token: {str(e)}")


def verify_access_token(token: str) -> Dict[str, Any]:
    """
    Verify an access token.

    Args:
        token: The access token to verify

    Returns:
        Token payload if valid

    Raises:
        JWTError: If token is invalid, expired, or not an access token
    """
    payload = decode_token(token)
    if payload.get("type") != "access":
        raise JWTError("Invalid token type")
    return payload


def verify_refresh_token(token: str) -> Dict[str, Any]:
    """
    Verify a refresh token.

    Args:
        token: The refresh token to verify

    Returns:
        Token payload if valid

    Raises:
        JWTError: If token is invalid, expired, or not a refresh token
    """
    payload = decode_token(token, settings.secret_key_refresh)
    if payload.get("type") != "refresh":
        raise JWTError("Invalid token type")
    return payload


# =============================================================================
# PHI Encryption
# =============================================================================
class PHIEncryption:
    """
    Handles encryption of Protected Health Information (PHI) at rest.

    Uses AES-256 encryption via Fernet (symmetric encryption).
    Compliant with HIPAA encryption requirements.
    """

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize the encryption handler.

        Args:
            encryption_key: 64-character hex string (32 bytes)
                           If None, uses settings.encryption_key
        """
        key = encryption_key or settings.encryption_key

        # Convert hex key to bytes
        key_bytes = bytes.fromhex(key)

        # Derive a proper Fernet key using PBKDF2
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"CareFlow_AI_PHI_Salt_v1",  # Fixed salt for reproducibility
            iterations=100000,
            backend=default_backend(),
        )
        derived_key = kdf.derive(key_bytes)

        # Fernet requires a base64-encoded key
        self._fernet = Fernet(urlsafe_b64encode(derived_key))
        self._key = key

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt PHI data.

        Args:
            plaintext: The sensitive data to encrypt

        Returns:
            URL-safe base64-encoded encrypted data
        """
        if not plaintext:
            return ""

        encrypted_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt PHI data.

        Args:
            ciphertext: The encrypted data to decrypt

        Returns:
            Decrypted plaintext

        Raises:
            ValueError: If decryption fails
        """
        if not ciphertext:
            return ""

        try:
            decrypted_bytes = self._fernet.decrypt(ciphertext.encode("utf-8"))
            return decrypted_bytes.decode("utf-8")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

    def encrypt_dict(self, data: Dict[str, Any], fields: list[str]) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.

        Args:
            data: Dictionary containing PHI
            fields: List of field names to encrypt

        Returns:
            Dictionary with specified fields encrypted
        """
        encrypted_data = data.copy()
        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        return encrypted_data

    def decrypt_dict(self, data: Dict[str, Any], fields: list[str]) -> Dict[str, Any]:
        """
        Decrypt specific fields in a dictionary.

        Args:
            data: Dictionary with encrypted PHI
            fields: List of field names to decrypt

        Returns:
            Dictionary with specified fields decrypted
        """
        decrypted_data = data.copy()
        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception:
                    # If decryption fails, leave as-is
                    pass
        return decrypted_data


# Global encryption instance
phi_encryption = PHIEncryption()


# =============================================================================
# Token Hashing for Verification
# =============================================================================
def hash_token(token: str) -> str:
    """
    Hash a token for storage (never store raw tokens).

    Args:
        token: The token to hash

    Returns:
        SHA-256 hash of the token
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def verify_token_hash(token: str, token_hash: str) -> bool:
    """
    Verify a token against its hash.

    Args:
        token: The token to verify
        token_hash: The stored hash to compare against

    Returns:
        True if token matches hash
    """
    return hmac.compare_digest(hash_token(token), token_hash)


# =============================================================================
# API Key Generation
# =============================================================================
def generate_api_key() -> tuple[str, str]:
    """
    Generate a new API key and its hash.

    Returns:
        Tuple of (api_key, api_key_hash)
        Store the hash, return the key to user
    """
    api_key = f"cf_{secrets.token_urlsafe(32)}"
    api_key_hash = hash_token(api_key)
    return api_key, api_key_hash


def verify_api_key(api_key: str, api_key_hash: str) -> bool:
    """
    Verify an API key.

    Args:
        api_key: The API key to verify
        api_key_hash: The stored hash

    Returns:
        True if API key is valid
    """
    return verify_token_hash(api_key, api_key_hash)
