"""
Invoice Service
"""

from datetime import date, datetime
from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice


async def create_invoice(
    db: AsyncSession,
    patient_id: UUID,
    items: list,
    created_by: UUID,
) -> Invoice:
    """Create a new invoice."""
    from app.models.invoice import InvoiceLine
    import random

    # Generate invoice number
    invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{random.randint(1000, 9999)}"

    invoice = Invoice(
        patient_id=patient_id,
        invoice_number=invoice_number,
        invoice_date=date.today(),
    )

    db.add(invoice)
    await db.flush()

    # Add line items
    total = 0
    for item in items:
        line = InvoiceLine(
            invoice_id=invoice.id,
            description=item["description"],
            quantity=item.get("quantity", 1),
            unit_price=item["unit_price"],
            amount=item["quantity"] * item["unit_price"],
        )
        db.add(line)
        total += line.amount

    invoice.total_amount = total
    invoice.balance_due = total

    await db.commit()
    await db.refresh(invoice)

    return invoice


async def get_invoices_by_patient(
    db: AsyncSession,
    patient_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Invoice], int]:
    """List invoices for a patient."""
    query = select(Invoice).where(Invoice.patient_id == patient_id)

    count_result = await db.execute(
        select(func.count(Invoice.id)).where(Invoice.patient_id == patient_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Invoice.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total
