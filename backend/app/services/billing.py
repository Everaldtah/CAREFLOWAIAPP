"""
Billing Service
"""

from typing import Optional
from uuid import UUID
from datetime import date

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice, Payment, PaymentStatus
from app.models.claim import Claim


async def get_revenue_summary(
    db: AsyncSession,
    clinic_id: UUID,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> dict:
    """Get revenue summary for a clinic."""
    from app.models.appointment import Appointment

    # Get total charges
    charges_result = await db.execute(
        select(func.sum(Appointment.fee)).where(
            Appointment.clinic_id == clinic_id
        )
    )
    total_charges = charges_result.scalar() or 0

    # Get total payments (simplified)
    total_payments = 0
    outstanding_balance = total_charges - total_payments

    return {
        "total_charges": float(total_charges),
        "total_payments": total_payments,
        "outstanding_balance": outstanding_balance,
        "collection_rate": 0.85,
    }


async def create_claim_from_encounter(
    db: AsyncSession,
    encounter_id: UUID,
    created_by: UUID,
) -> Claim:
    """Create insurance claim from encounter."""
    from app.models.encounter import Encounter

    result = await db.execute(
        select(Encounter).where(Encounter.id == encounter_id)
    )
    encounter = result.scalar_one_or_none()

    if not encounter:
        raise ValueError("Encounter not found")

    claim = Claim(
        encounter_id=encounter_id,
        patient_id=encounter.patient_id,
        date_of_service=encounter.start_time.date(),
        total_charge=100.0,  # Simplified
        submitted_by_id=created_by,
    )

    db.add(claim)
    await db.commit()
    await db.refresh(claim)

    return claim


async def process_payment(
    db: AsyncSession,
    invoice_id: UUID,
    amount: float,
    payment_method: str,
    processed_by: UUID,
) -> Payment:
    """Process a payment for an invoice."""
    payment = Payment(
        invoice_id=invoice_id,
        amount=amount,
        payment_method=payment_method,
        status=PaymentStatus.COMPLETED,
        processed_by_id=processed_by,
    )

    db.add(payment)

    # Update invoice balance
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
    )
    invoice = result.scalar_one_or_none()

    if invoice:
        invoice.balance_due -= amount
        if invoice.balance_due <= 0:
            invoice.status = "paid"

    await db.commit()
    await db.refresh(payment)

    return payment
