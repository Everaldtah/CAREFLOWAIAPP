"""
Dashboard Service

Provides analytics and summary data for dashboards.
"""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.models.appointment import Appointment, AppointmentStatus
from app.models.user import User


async def get_overview_stats(
    db: AsyncSession,
    clinic_id,
) -> dict:
    """Get dashboard overview statistics."""
    # Total patients
    patient_result = await db.execute(
        select(func.count(Patient.id)).where(Patient.clinic_id == clinic_id)
    )
    total_patients = patient_result.scalar() or 0

    # Appointments today
    today = datetime.now().date()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    appt_result = await db.execute(
        select(func.count(Appointment.id)).where(
            (Appointment.clinic_id == clinic_id) &
            (Appointment.start_time >= today_start) &
            (Appointment.start_time <= today_end)
        )
    )
    appointments_today = appt_result.scalar() or 0

    # Active providers
    provider_result = await db.execute(
        select(func.count(User.id)).where(
            (User.clinic_id == clinic_id) &
            (User.role == "provider") &
            (User.is_active == True)
        )
    )
    active_providers = provider_result.scalar() or 0

    return {
        "total_patients": total_patients,
        "appointments_today": appointments_today,
        "active_providers": active_providers,
        "revenue_this_month": 0,  # Placeholder
    }


async def get_appointment_statistics(
    db: AsyncSession,
    clinic_id,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    """Get appointment statistics for date range."""
    result = await db.execute(
        select(
            Appointment.status,
            func.count(Appointment.id).label("count"),
        )
        .where(
            (Appointment.clinic_id == clinic_id) &
            (Appointment.start_time >= start_date) &
            (Appointment.start_time <= end_date)
        )
        .group_by(Appointment.status)
    )

    stats = {status: 0 for status in ["pending", "confirmed", "completed", "cancelled", "no_show"]}
    for row in result:
        stats[row.status] = row.count

    return {
        "by_status": stats,
        "total": sum(stats.values()),
        "show_rate": calculate_show_rate(stats),
    }


async def get_patient_statistics(
    db: AsyncSession,
    clinic_id,
) -> dict:
    """Get patient statistics."""
    # New patients this month
    this_month = datetime.now().replace(day=1)
    new_result = await db.execute(
        select(func.count(Patient.id)).where(
            (Patient.clinic_id == clinic_id) &
            (Patient.created_at >= this_month)
        )
    )
    new_patients = new_result.scalar() or 0

    return {
        "new_this_month": new_patients,
        "active": 0,  # Would calculate based on visits
    }


async def get_revenue_statistics(
    db: AsyncSession,
    clinic_id,
    period: str = "month",
) -> dict:
    """Get revenue statistics."""
    return {
        "total_revenue": 0,
        "outstanding": 0,
        "collection_rate": 0.85,
    }


async def get_ai_performance_metrics(
    db: AsyncSession,
    clinic_id,
    start_date: datetime,
    end_date: datetime,
) -> dict:
    """Get AI agent performance metrics."""
    return {
        "triage_accuracy": 0.92,
        "scheduling_efficiency": 0.88,
        "scribe_adoption": 0.75,
        "patient_satisfaction": 4.5,
    }


async def get_alerts(
    db: AsyncSession,
    clinic_id,
    user_id,
) -> List[dict]:
    """Get dashboard alerts."""
    return [
        {
            "type": "info",
            "message": "3 appointments pending confirmation",
            "action_url": "/appointments?status=pending",
        }
    ]


def calculate_show_rate(stats: dict) -> float:
    """Calculate patient show rate."""
    completed = stats.get("completed", 0)
    no_show = stats.get("no_show", 0)
    total = completed + no_show

    if total == 0:
        return 1.0

    return completed / total
