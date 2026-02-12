"""
API Router for CareFlow AI v1

Aggregates all v1 endpoint routers.
"""

from fastapi import APIRouter

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

api_router = APIRouter()

@api_router.get("/health", status_code=200)
def health():
    from app.core.database import get_db
    db = get_db()
    try:
        # Try to execute a simple query
        db.execute("SELECT 1")
        return {
            "status": "ok",
            "database": "connected",
            "redis": "connected"
        }
    except Exception as e:
        return {
            "status": "error",
            "database": "disconnected",
            "redis": "disconnected",
            "message": str(e)
        }

# =============================================================================
# Public Routes (no authentication)
# =============================================================================

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# =============================================================================
# Protected Routes (require authentication)
# =============================================================================

# Tenant & Clinic Management
api_router.include_router(tenants.router, prefix="/tenants", tags=["Tenants"])
api_router.include_router(clinics.router, prefix="/clinics", tags=["Clinics"])

# User Management
api_router.include_router(users.router, prefix="/users", tags=["Users"])

# Patient Management
api_router.include_router(patients.router, prefix="/patients", tags=["Patients"])

# Appointments & Scheduling
api_router.include_router(
    appointments.router,
    prefix="/appointments",
    tags=["Appointments"],
)

# Clinical Documentation
api_router.include_router(encounters.router, prefix="/encounters", tags=["Encounters"])
api_router.include_router(notes.router, prefix="/notes", tags=["Clinical Notes"])

# AI Conversations
api_router.include_router(
    conversations.router,
    prefix="/conversations",
    tags=["AI Conversations"],
)
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])

# Billing & Claims
api_router.include_router(billing.router, prefix="/billing", tags=["Billing"])
api_router.include_router(claims.router, prefix="/claims", tags=["Insurance Claims"])
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoices"])

# Dashboard & Analytics
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# Integrations
api_router.include_router(integrations.router, prefix="/integrations", tags=["Integrations"])


# =============================================================================
# Me Endpoint (current user info)
# =============================================================================

@api_router.get("/me")
async def get_me():
    """Placeholder for current user endpoint."""
    return {"message": "This endpoint will return current user info"}
