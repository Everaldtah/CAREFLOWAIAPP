"""
Patient endpoint tests
"""

import pytest
from datetime import date


def test_create_patient(test_client, auth_headers):
    """Test creating a new patient."""
    response = test_client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "date_of_birth": "1980-01-15",
            "gender": "male",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert data["email"] == "john.doe@example.com"
    assert "id" in data


def test_list_patients(test_client, auth_headers):
    """Test listing patients."""
    # Create a patient first
    test_client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane@example.com",
        },
    )

    # List patients
    response = test_client.get("/api/v1/patients", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert len(data["items"]) > 0


def test_get_patient(test_client, auth_headers):
    """Test getting a specific patient."""
    # Create a patient
    create_response = test_client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "first_name": "Bob",
            "last_name": "Johnson",
            "email": "bob@example.com",
        },
    )

    patient_id = create_response.json()["id"]

    # Get patient
    response = test_client.get(f"/api/v1/patients/{patient_id}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["first_name"] == "Bob"
    assert data["last_name"] == "Johnson"


def test_update_patient(test_client, auth_headers):
    """Test updating a patient."""
    # Create a patient
    create_response = test_client.post(
        "/api/v1/patients",
        headers=auth_headers,
        json={
            "first_name": "Alice",
            "last_name": "Williams",
            "email": "alice@example.com",
        },
    )

    patient_id = create_response.json()["id"]

    # Update patient
    response = test_client.patch(
        f"/api/v1/patients/{patient_id}",
        headers=auth_headers,
        json={
            "phone": "555-999-8888",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["phone"] == "555-999-8888"


def test_search_patients(test_client, auth_headers):
    """Test searching for patients."""
    response = test_client.get(
        "/api/v1/patients/search?query=John",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
