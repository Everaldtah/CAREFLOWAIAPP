"""
Billing Agent

AI agent for medical billing and coding assistance.
"""

import logging
from typing import Any, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.claim import Claim
from app.models.encounter import Encounter

logger = logging.getLogger(__name__)


class BillingAgent:
    """
    AI agent for billing and coding assistance.

    Features:
    - Suggest ICD-10 diagnosis codes
    - Suggest CPT procedure codes
    - Validate claims before submission
    - Check for common errors
    """

    def __init__(self, db: AsyncSession):
        """
        Initialize the billing agent.

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
        Process a billing inquiry.

        Args:
            message: User's billing question
            conversation_id: Conversation ID

        Returns:
            Response dict
        """
        return {
            "content": (
                "I can help you with billing questions. "
                "Would you like information about:\n"
                "- Your outstanding balance\n"
                "- Insurance coverage\n"
                "- Payment options\n"
                "- Understanding your bill"
            ),
            "metadata": {"agent": "billing"},
        }

    async def suggest_codes(
        self,
        encounter_id: UUID,
        diagnosis_text: Optional[str] = None,
        procedure_text: Optional[str] = None,
        transcript: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Suggest billing codes for an encounter.

        Args:
            encounter_id: Encounter ID
            diagnosis_text: Diagnosis description
            procedure_text: Procedure description
            transcript: Visit transcript

        Returns:
            Suggested codes with confidence scores
        """
        # Get encounter details
        result = await self.db.execute(
            select(Encounter).where(Encounter.id == encounter_id)
        )
        encounter = result.scalar_one_or_none()

        if not encounter:
            return {"error": "Encounter not found"}

        # In production, would use LLM to analyze:
        # - Chief complaint
        # - Assessment
        # - Plan
        # - Procedures performed

        # Example ICD-10 codes
        icd_10_suggestions = [
            {
                "code": "R06.02",
                "description": "Shortness of breath",
                "confidence": 0.85,
            },
            {
                "code": "J06.9",
                "description": "Acute upper respiratory infection, unspecified",
                "confidence": 0.72,
            },
        ]

        # Example CPT codes
        cpt_suggestions = [
            {
                "code": "99213",
                "description": "Office visit, established patient, low complexity",
                "confidence": 0.90,
            },
        ]

        return {
            "icd_10_codes": icd_10_suggestions,
            "cpt_codes": cpt_suggestions,
            "confidence": 0.82,
            "reasoning": "Based on documented chief complaint and assessment",
        }

    async def validate_claim(
        self,
        claim_id: UUID,
    ) -> dict[str, Any]:
        """
        Validate a claim before submission.

        Args:
            claim_id: Claim ID

        Returns:
            Validation results
        """
        # Get claim
        result = await self.db.execute(
            select(Claim).where(Claim.id == claim_id)
        )
        claim = result.scalar_one_or_none()

        if not claim:
            return {
                "is_valid": False,
                "errors": ["Claim not found"],
                "warnings": [],
            }

        errors = []
        warnings = []

        # Check required fields
        if not claim.date_of_service:
            errors.append("Date of service is required")

        if not claim.patient_id:
            errors.append("Patient ID is required")

        if not claim.total_charge or claim.total_charge <= 0:
            errors.append("Total charge must be greater than 0")

        # Check for common issues
        if claim.total_charge > 10000:
            warnings.append("High charge amount - please verify")

        # Check if claim has line items
        # (Would check claim.lines in production)

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }
