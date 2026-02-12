"""
API v1 Endpoints Package
"""

from app.api.v1.endpoints import (
    auth,
    tenants,
    clinics,
    users,
    patients,
    appointments,
    encounters,
    notes,
    conversations,
    messages,
    billing,
    claims,
    invoices,
    dashboard,
    integrations,
)

__all__ = [
    "auth",
    "tenants",
    "clinics",
    "users",
    "patients",
    "appointments",
    "encounters",
    "notes",
    "conversations",
    "messages",
    "billing",
    "claims",
    "invoices",
    "dashboard",
    "integrations",
]
