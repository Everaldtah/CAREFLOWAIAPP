"""
Core Configuration Module for CareFlow AI

Loads and validates all environment variables using Pydantic Settings.
All sensitive values are loaded from environment variables.
"""

import secrets
from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # =============================================================================
    # Application
    # =============================================================================
    app_name: str = "CareFlow AI"
    app_env: Literal["development", "staging", "production"] = "development"
    app_debug: bool = False
    app_version: str = "1.0.0"
    app_url: str = "http://localhost:3000"
    api_url: str = "http://localhost:8000"
    api_v1_prefix: str = "/api/v1"

    # =============================================================================
    # Security
    # =============================================================================
    secret_key: str = Field(
        default=secrets.token_urlsafe(32),
        description="Secret key for JWT signing",
    )
    secret_key_refresh: str = Field(
        default=secrets.token_urlsafe(32),
        description="Secret key for refresh token signing",
    )
    encryption_key: str = Field(
        ..., description="AES-256 encryption key for PHI at rest (32 bytes hex)"
    )

    # JWT Configuration
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    jwt_algorithm: str = "HS256"

    # Password requirements
    password_min_length: int = 8
    password_require_uppercase: bool = True
    password_require_lowercase: bool = True
    password_require_digit: bool = True
    password_require_special: bool = True

    # =============================================================================
    # Database
    # =============================================================================
    database_url: str = Field(
        ..., description="PostgreSQL connection URL"
    )
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_recycle: int = 3600

    # =============================================================================
    # Redis
    # =============================================================================
    redis_url: str = Field(
        ..., description="Redis connection URL for main operations"
    )
    redis_cache_url: str = Field(
        ..., description="Redis connection URL for caching"
    )
    redis_agent_state_url: str = Field(
        ..., description="Redis connection URL for agent state"
    )

    # =============================================================================
    # AI/LLM Configuration
    # =============================================================================
    llm_provider: Literal["openai", "anthropic"] = "openai"
    llm_model: str = "gpt-4-turbo-preview"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    llm_timeout: int = 60

    # OpenAI
    openai_api_key: Optional[str] = None

    # Anthropic
    anthropic_api_key: Optional[str] = None

    # Vector Database
    vector_dimensions: int = 1536
    vector_similarity_threshold: float = 0.75

    # =============================================================================
    # Email
    # =============================================================================
    smtp_host: str = "smtp.resend.com"
    smtp_port: int = 587
    smtp_user: str = "resend"
    smtp_password: str = ""
    smtp_from: str = "noreply@careflow.ai"
    smtp_from_name: str = "CareFlow AI"
    smtp_use_tls: bool = True

    # =============================================================================
    # Storage
    # =============================================================================
    storage_driver: Literal["s3", "minio", "local"] = "local"
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    aws_s3_bucket: str = "careflow-documents"
    local_storage_path: str = "./uploads"

    # =============================================================================
    # OAuth/Social
    # =============================================================================
    google_oauth_client_id: Optional[str] = None
    google_oauth_client_secret: Optional[str] = None
    microsoft_oauth_client_id: Optional[str] = None
    microsoft_oauth_client_secret: Optional[str] = None

    # =============================================================================
    # Monitoring
    # =============================================================================
    sentry_dsn: Optional[str] = None
    sentry_environment: str = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    # OpenTelemetry
    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_service_name: str = "careflow-ai"

    # =============================================================================
    # Rate Limiting
    # =============================================================================
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60
    rate_limit_burst: int = 100

    # =============================================================================
    # Feature Flags
    # =============================================================================
    feature_ai_triage_enabled: bool = True
    feature_ai_scribe_enabled: bool = True
    feature_ai_billing_enabled: bool = True
    feature_auto_scheduling_enabled: bool = True
    feature_telehealth_enabled: bool = False

    # =============================================================================
    # Compliance
    # =============================================================================
    compliance_retention_days: int = 2555  # 7 years
    compliance_audit_log_retention_days: int = 2555
    compliance_anonymize_after_retention: bool = True

    # =============================================================================
    # Multi-tenancy
    # =============================================================================
    tenant_isolation_level: Literal["database", "schema", "row"] = "database"
    max_clinics_per_tenant: int = 100
    max_users_per_clinic: int = 500

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Validate encryption key is exactly 64 hex characters (32 bytes)."""
        if len(v) != 64:
            raise ValueError("ENCRYPTION_KEY must be exactly 64 hexadecimal characters (32 bytes)")
        try:
            bytes.fromhex(v)
        except ValueError:
            raise ValueError("ENCRYPTION_KEY must contain only hexadecimal characters")
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.app_env == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development."""
        return self.app_env == "development"

    @property
    def database_url_async(self) -> str:
        """Convert postgres:// URL to postgresql+asyncpg:// format."""
        return self.database_url.replace("postgresql://", "postgresql+asyncpg://")

    @property
    def cors_origins(self) -> list[str]:
        """Get CORS allowed origins based on environment."""
        if self.is_production:
            return [self.app_url]
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This function is cached to avoid reloading environment variables.
    """
    return Settings()


# Global settings instance
settings = get_settings()
