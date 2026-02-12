"""
Seed Database Script

Populates the database with initial data for development.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User, Role
from app.models.tenant import Tenant, Plan
from app.models.clinic import Clinic


async def seed_database():
    """Seed the database with initial data."""
    async with AsyncSessionLocal() as db:
        try:
            # Create a demo tenant
            tenant = Tenant(
                name="Demo Healthcare",
                slug="demo-healthcare",
                plan=Plan.PROFESSIONAL,
            )
            db.add(tenant)
            await db.flush()

            # Create a demo clinic
            clinic = Clinic(
                tenant_id=tenant.id,
                name="Demo Family Medicine",
                address="123 Main St, Anytown, USA 12345",
                phone="555-123-4567",
                email="info@democlinic.com",
            )
            db.add(clinic)
            await db.flush()

            # Create admin user
            admin_user = User(
                tenant_id=tenant.id,
                clinic_id=clinic.id,
                email="admin@careflow.ai",
                hashed_password=get_password_hash("Admin123!"),
                first_name="System",
                last_name="Administrator",
                role=Role.ADMIN,
                is_active=True,
                is_verified=True,
            )
            db.add(admin_user)
            await db.flush()

            # Create provider user
            provider_user = User(
                tenant_id=tenant.id,
                clinic_id=clinic.id,
                email="doctor@careflow.ai",
                hashed_password=get_password_hash("Doctor123!"),
                first_name="Sarah",
                last_name="Johnson",
                role=Role.PROVIDER,
                npi="1234567890",
                specialization="Family Medicine",
                is_active=True,
                is_verified=True,
            )
            db.add(provider_user)
            await db.flush()

            # Create patient user
            patient_user = User(
                tenant_id=tenant.id,
                clinic_id=clinic.id,
                email="patient@example.com",
                hashed_password=get_password_hash("Patient123!"),
                first_name="John",
                last_name="Smith",
                role=Role.PATIENT,
                is_active=True,
                is_verified=True,
            )
            db.add(patient_user)

            await db.commit()

            print("✅ Database seeded successfully!")
            print("\nDemo Accounts:")
            print("  Admin: admin@careflow.ai / Admin123!")
            print("  Provider: doctor@careflow.ai / Doctor123!")
            print("  Patient: patient@example.com / Patient123!")

        except Exception as e:
            await db.rollback()
            print(f"❌ Error seeding database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(seed_database())
