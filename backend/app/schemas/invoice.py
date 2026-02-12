from enum import Enum
"""
Invoice Schemas
"""

from datetime import date, datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr


class InvoiceStatus(str, Enum):
    """Invoice status."""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    WRITTEN_OFF = "written_off"
    CANCELLED = "cancelled"


class InvoiceLineCreate(BaseModel):
    """Request schema for creating an invoice line."""
    description: str
    quantity: int = 1
    unit_price: float
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None


class InvoiceCreate(BaseModel):
    """Request schema for creating an invoice."""
    patient_id: UUID
    items: List[InvoiceLineCreate]
    due_date: Optional[date] = None
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    """Response schema for invoice."""
    id: UUID
    patient_id: UUID
    invoice_number: str
    status: str
    invoice_date: date
    due_date: Optional[date]
    subtotal: float
    tax_amount: float
    discount_amount: float
    total_amount: float
    balance_due: float
    created_at: datetime
    updated_at: datetime
