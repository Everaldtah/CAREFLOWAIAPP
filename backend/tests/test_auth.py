"""
Authentication endpoint tests
"""

import pytest


def test_register_user(test_client):
    """Test user registration."""
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["first_name"] == "New"
    assert "id" in data


def test_register_duplicate_email(test_client):
    """Test registration with duplicate email fails."""
    # First registration
    test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "first_name": "First",
            "last_name": "User",
        },
    )

    # Duplicate registration
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "SecurePass123!",
            "first_name": "Second",
            "last_name": "User",
        },
    )

    assert response.status_code == 400


def test_login_success(test_client):
    """Test successful login."""
    # Register first
    test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "LoginPass123!",
            "first_name": "Login",
            "last_name": "User",
        },
    )

    # Login
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "LoginPass123!",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(test_client):
    """Test login with invalid credentials."""
    response = test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "WrongPass123!",
        },
    )

    assert response.status_code == 401


def test_get_current_user(test_client, auth_headers):
    """Test getting current user info."""
    response = test_client.get("/api/v1/auth/me", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "first_name" in data
    assert "last_name" in data
