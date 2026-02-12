"""
Invoice and Payment Models

Patient billing and payment tracking.
"""

import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import String, Date, DateTime, Text, ForeignKey, Enum as SQLEnum, Numeric, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class InvoiceStatus(str, Enum):
    """Invoice status."""
    DRAFT = "draft"
    SENT = "sent"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    WRITTEN_OFF = "written_off"
    CANCELLED = "cancelled"


class Invoice(BaseModel):
    """
    Patient invoice model.

    Tracks amounts owed by patients for services.
    """

    # Foreign Keys
    patient_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Invoice Details
    invoice_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    status: Mapped[InvoiceStatus] = mapped_column(
        SQLEnum(InvoiceStatus),
        default=InvoiceStatus.DRAFT,
        nullable=False,
        index=True,
    )

    # Dates
    invoice_date: Mapped[date] = mapped_column(Date(), nullable=False, default=date.today)
    due_date: Mapped[date | None] = mapped_column(Date())

    # Financials
    subtotal: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    tax_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    discount_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)
    balance_due: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=0)

    # Notes
    notes: Mapped[str | None] = mapped_column(Text())
    internal_notes: Mapped[str | None] = mapped_column(Text())

    # Relationships
    patient = relationship("Patient", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="invoice", cascade="all, delete-orphan")

    @property
    def is_paid(self) -> bool:
        """Check if invoice is fully paid."""
        return self.status == InvoiceStatus.PAID or self.balance_due <= 0

    def __repr__(self) -> str:
        return f"<Invoice(id={self.id}, number='{self.invoice_number}', balance={self.balance_due})>"


class InvoiceLine(BaseModel):
    """
    Individual line items within an invoice.
    """

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Line Details
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(default=1)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    # Reference
    reference_type: Mapped[str | None] = mapped_column(String(50))  # 'appointment', 'procedure', etc.
    reference_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # Relationships
    invoice = relationship("Invoice", back_populates="lines")

    def __repr__(self) -> str:
        return f"<InvoiceLine(id={self.id}, description='{self.description}', amount={self.amount})>"


class PaymentMethod(str, Enum):
    """Payment methods."""
    CASH = "cash"
    CHECK = "check"
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    ACH = "ach"
    INSURANCE = "insurance"
    WRITE_OFF = "write_off"


class PaymentStatus(str, Enum):
    """Payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Payment(BaseModel):
    """
    Payment model.

    Tracks payments received from patients or insurance.
    """

    # Foreign Keys
    invoice_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("invoices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Payment Details
    payment_date: Mapped[date] = mapped_column(Date(), nullable=False, default=date.today)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_method: Mapped[PaymentMethod] = mapped_column(
        SQLEnum(PaymentMethod),
        nullable=False,
    )
    status: Mapped[PaymentStatus] = mapped_column(
        SQLEnum(PaymentStatus),
        default=PaymentStatus.PENDING,
        nullable=False,
    )

    # Reference
    reference_number: Mapped[str | None] = mapped_column(String(100))  # Check #, transaction ID, etc.
    notes: Mapped[str | None] = mapped_column(Text())

    # Processing
    processed_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Gateway Response
    gateway_response: Mapped[dict | None] = mapped_column(JSON)

    # Relationships
    invoice = relationship("Invoice", back_populates="payments")

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, amount={self.amount}, method='{self.payment_method}')>"
