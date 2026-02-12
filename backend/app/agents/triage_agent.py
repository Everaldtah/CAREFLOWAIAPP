"""
Triage Agent

AI agent for patient symptom assessment and triage.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.patient import Patient
from app.models.conversation import Conversation
from app.core.config import settings

logger = logging.getLogger(__name__)


class TriageAgent:
    """
    AI agent for symptom triage and urgency assessment.

    Assesses patient symptoms and recommends appropriate action:
    - Emergency care (call 911)
    - Urgent care visit
    - Scheduled appointment
    - Home care
    """

    # Urgency levels
    URGENCY_EMERGENCY = "emergency"
    URGENCY_URGENT = "urgent"
    URGENCY_SCHEDULED = "scheduled"
    URGENCY_HOME_CARE = "home_care"

    def __init__(self, db: AsyncSession):
        """
        Initialize the triage agent.

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
        Process a triage request.

        Args:
            message: Patient's description of symptoms
            conversation_id: Conversation ID for context

        Returns:
            Response dict with content and metadata
        """
        # Analyze symptoms (simplified - would use LLM in production)
        urgency, recommended_action = await self._assess_urgency(message)

        response_content = self._format_response(urgency, recommended_action, message)

        return {
            "content": response_content,
            "metadata": {
                "urgency": urgency,
                "recommended_action": recommended_action,
                "agent": "triage",
            },
            "escalated": urgency == self.URGENCY_EMERGENCY,
        }

    async def assess(
        self,
        patient_id: UUID,
        symptoms: str,
    ) -> dict[str, Any]:
        """
        Assess symptoms for a patient.

        Args:
            patient_id: Patient ID
            symptoms: Symptom description

        Returns:
            Assessment results
        """
        urgency, recommended_action = await self._assess_urgency(symptoms)

        return {
            "urgency": urgency,
            "recommended_action": recommended_action,
            "symptoms": symptoms,
        }

    async def _assess_urgency(self, symptoms: str) -> tuple[str, str]:
        """
        Assess urgency level from symptoms.

        Args:
            symptoms: Symptom description

        Returns:
            Tuple of (urgency_level, recommended_action)
        """
        symptoms_lower = symptoms.lower()

        # Emergency indicators
        emergency_keywords = [
            "chest pain", "heart attack", "stroke", "difficulty breathing",
            "can't breathe", "short of breath", "severe bleeding", "loss of consciousness",
            "unconscious", "fainted", "severe burn", "head trauma", "suicide",
            "kill myself", "overdose", "allergic reaction", "swallow tongue",
        ]

        for keyword in emergency_keywords:
            if keyword in symptoms_lower:
                return self.URGENCY_EMERGENCY, "call_911"

        # Urgent care indicators
        urgent_keywords = [
            "high fever", "severe pain", "broken bone", "fracture",
            "deep cut", "stitches", "vomiting blood", "severe headache",
            "sudden vision", "abdominal pain",
        ]

        for keyword in urgent_keywords:
            if keyword in symptoms_lower:
                return self.URGENCY_URGENT, "urgent_care"

        # Schedule appointment indicators
        scheduled_keywords = [
            "checkup", "physical", "follow up", "consultation",
            "routine", "medication refill",
        ]

        for keyword in scheduled_keywords:
            if keyword in symptoms_lower:
                return self.URGENCY_SCHEDULED, "schedule_appointment"

        # Default to scheduled appointment
        return self.URGENCY_SCHEDULED, "schedule_appointment"

    def _format_response(self, urgency: str, action: str, symptoms: str) -> str:
        """
        Format a response to the patient.

        Args:
            urgency: Urgency level
            action: Recommended action
            symptoms: Original symptoms

        Returns:
            Formatted response message
        """
        if urgency == self.URGENCY_EMERGENCY:
            return (
                "⚠️ Based on your symptoms, this appears to be a medical emergency. "
                "Please call 911 or go to the nearest emergency room immediately. "
                "Do not wait."
            )

        elif urgency == self.URGENCY_URGENT:
            return (
                "Based on your symptoms, I recommend visiting an urgent care center "
                "today. Your symptoms should be evaluated by a healthcare provider soon. "
                "Would you like me to help you find an urgent care location?"
            )

        elif urgency == self.URGENCY_SCHEDULED:
            return (
                "Thank you for describing your symptoms. Based on what you've shared, "
                "I recommend scheduling an appointment with a healthcare provider. "
                "Would you like me to help you book an appointment?"
            )

        else:
            return (
                "Thank you for reaching out. Based on your symptoms, home care may be "
                "appropriate. However, if your symptoms worsen or you have concerns, "
                "please don't hesitate to seek medical care. Would you like me to "
                "help you schedule a consultation?"
            )
