"""
Scheduling Agent

AI agent for appointment scheduling and calendar optimization.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.appointment import Appointment, AppointmentStatus, AppointmentType
from app.models.user import User

logger = logging.getLogger(__name__)


class SchedulingAgent:
    """
    AI agent for intelligent appointment scheduling.

    Features:
    - Finds optimal time slots
    - Minimizes gaps in provider schedule
    - Considers patient preferences
    - Predicts no-shows
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the scheduling agent.

        Args:
            db: Database session
        """
        self.db = db

    async def process(
        self,
        message: str,
        conversation_id: UUID,
    ) -> dict[str, Any]:
        """
        Process a scheduling request.

        Args:
            message: User's scheduling request
            conversation_id: Conversation ID

        Returns:
            Response dict
        """
        # This is a simplified version
        # In production, would use LLM to extract:
        # - Preferred date/time
        # - Appointment type
        # - Provider preference

        return {
            "content": (
                "I'd be happy to help you schedule an appointment. "
                "To find the best time for you, could you please tell me:\n"
                "1. What type of appointment do you need?\n"
                "2. What day works best for you?\n"
                "3. Do you have a preferred provider?"
            ),
            "metadata": {"agent": "scheduling"},
        }

    async def suggest_slots(
        self,
        clinic_id: UUID,
        patient_id: UUID,
        appointment_type: str,
        duration_minutes: int,
        preferred_dates: list[str],
    ) -> list[dict[str, Any]]:
        """
        Suggest available appointment slots.

        Args:
            clinic_id: Clinic ID
            patient_id: Patient ID
            appointment_type: Type of appointment
            duration_minutes: Duration in minutes
            preferred_dates: List of preferred date strings

        Returns:
            List of suggested time slots
        """
        # In production, this would:
        # 1. Query provider availability
        # 2. Check for conflicts
        # 3. Optimize for minimal gaps
        # 4. Consider no-show predictions

        suggestions = []

        # Simplified example suggestions
        for date_str in preferred_dates[:3]:
            suggestions.append({
                "date": date_str,
                "time": "10:00 AM",
                "provider": "Dr. Smith",
                "availability": "available",
            })

        return suggestions

    async def optimize_schedule(
        self,
        provider_id: UUID,
        date: datetime,
    ) -> dict[str, Any]:
        """
        Optimize a provider's schedule for a given day.

        Args:
            provider_id: Provider ID
            date: Date to optimize

        Returns:
            Optimization recommendations
        """
        # Get existing appointments
        result = await self.db.execute(
            select(Appointment).where(
                and_(
                    Appointment.provider_id == provider_id,
                    Appointment.start_time >= date.replace(hour=0, minute=0, second=0),
                    Appointment.start_time <= date.replace(hour=23, minute=59, second=59),
                    Appointment.status.in_([
                        AppointmentStatus.CONFIRMED,
                        AppointmentStatus.PENDING,
                    ]),
                )
            )
        )
        appointments = result.scalars().all()

        # Analyze gaps and suggest optimizations
        gaps = self._find_gaps(appointments)

        return {
            "provider_id": str(provider_id),
            "date": date.date().isoformat(),
            "existing_appointments": len(appointments),
            "gaps_found": len(gaps),
            "optimization_suggestions": gaps,
        }

    def _find_gaps(self, appointments: list[Appointment]) -> list[dict]:
        """
        Find gaps in a schedule.

        Args:
            appointments: List of appointments

        Returns:
            List of gap information
        """
        gaps = []
        sorted_appts = sorted(appointments, key=lambda a: a.start_time)

        for i in range(len(sorted_appts) - 1):
            current_end = sorted_appts[i].end_time
            next_start = sorted_appts[i + 1].start_time
            gap_minutes = (next_start - current_end).total_seconds() / 60

            if gap_minutes >= 15:  # Only significant gaps
                gaps.append({
                    "start": current_end.strftime("%I:%M %p"),
                    "end": next_start.strftime("%I:%M %p"),
                    "duration_minutes": int(gap_minutes),
                    "can_fit_appointments": self._max_appointment_in_gap(gap_minutes),
                })

        return gaps

    def _max_appointment_in_gap(self, gap_minutes: float) -> list[int]:
        """Determine what appointment lengths fit in a gap."""
        standard_lengths = [15, 30, 45, 60]
        return [length for length in standard_lengths if length <= gap_minutes]
