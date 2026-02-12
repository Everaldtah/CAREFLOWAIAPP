"""
Invoices Endpoints
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, Pagination
from app.schemas.invoice import InvoiceCreate, InvoiceResponse
from app.services.invoice import (
    create_invoice,
    get_invoice_by_id,
    get_invoices_by_patient,
    process_payment,
)

router = APIRouter()


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice_endpoint(
    data: InvoiceCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Create a new invoice."""
    invoice = await create_invoice(
        db=db,
        patient_id=data.patient_id,
        items=data.items,
        created_by=current_user.id,
    )
    return invoice


@router.get("/")
async def list_invoices(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
    patient_id: UUID | None = None,
) -> Any:
    """List invoices."""
    if patient_id:
        invoices, total = await get_invoices_by_patient(
            db=db,
            patient_id=patient_id,
            skip=pagination.skip,
            limit=pagination.limit,
        )
    else:
        # Get clinic invoices
        invoices, total = [], 0

    return {"items": invoices, "total": total}


@router.post("/{invoice_id}/pay")
async def pay_invoice(
    invoice_id: UUID,
    amount: float,
    payment_method: str,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """Process a payment for an invoice."""
    payment = await process_payment(
        db=db,
        invoice_id=invoice_id,
        amount=amount,
        payment_method=payment_method,
        processed_by=current_user.id,
    )
    return payment
