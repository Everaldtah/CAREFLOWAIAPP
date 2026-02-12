"""
Dashboard & Analytics Endpoints
"""

from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get dashboard overview statistics.

    - Patient counts
    - Appointments today
    - Revenue summary
    - Active tasks
    """
    from app.services.dashboard import get_overview_stats

    stats = await get_overview_stats(
        db=db,
        clinic_id=current_user.clinic_id,
    )

    return stats


@router.get("/appointments/stats")
async def get_appointment_stats(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
) -> Any:
    """
    Get appointment statistics for date range.
    """
    from app.services.dashboard import get_appointment_statistics

    stats = await get_appointment_statistics(
        db=db,
        clinic_id=current_user.clinic_id,
        start_date=start_date,
        end_date=end_date,
    )

    return stats


@router.get("/patients/stats")
async def get_patient_stats(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get patient statistics.

    - New patients (this month)
    - Active patients
    - Patient demographics
    """
    from app.services.dashboard import get_patient_statistics

    stats = await get_patient_statistics(
        db=db,
        clinic_id=current_user.clinic_id,
    )

    return stats


@router.get("/revenue/stats")
async def get_revenue_stats(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    period: str = Query("month", description="Period: week, month, quarter, year"),
) -> Any:
    """
    Get revenue statistics.

    - Total revenue
    - Outstanding balances
    - Collection rate
    - Top procedures
    """
    from app.services.dashboard import get_revenue_statistics

    stats = await get_revenue_statistics(
        db=db,
        clinic_id=current_user.clinic_id,
        period=period,
    )

    return stats


@router.get("/ai/performance")
async def get_ai_performance(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
) -> Any:
    """
    Get AI agent performance metrics.

    - Triage accuracy
    - Scheduling efficiency
    - Scribe adoption
    - Patient satisfaction
    """
    from app.services.dashboard import get_ai_performance_metrics

    metrics = await get_ai_performance_metrics(
        db=db,
        clinic_id=current_user.clinic_id,
        start_date=start_date,
        end_date=end_date,
    )

    return metrics


@router.get("/alerts")
async def get_dashboard_alerts(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get dashboard alerts and notifications.

    - Overdue follow-ups
    - Pending actions
    - System alerts
    """
    from app.services.dashboard import get_alerts

    alerts = await get_alerts(
        db=db,
        clinic_id=current_user.clinic_id,
        user_id=current_user.id,
    )

    return {"alerts": alerts}
