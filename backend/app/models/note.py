"""
Note Model

Clinical documentation including SOAP notes.
"""

import uuid
from enum import Enum

from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class NoteType(str, Enum):
    """Types of clinical notes."""
    SOAP = "soap"  # Subjective, Objective, Assessment, Plan
    PROGRESS = "progress_note"
    CONSULTATION = "consultation"
    PROCEDURE = "procedure_note"
    DISCHARGE = "discharge_summary"
    TELEPHONE = "telephone_note"
    EMAIL = "email_note"
    OTHER = "other"


class Note(BaseModel):
    """
    Clinical note model.

    Supports various note formats including SOAP notes.
    Content is stored as structured JSON.
    """

    # Foreign Keys
    encounter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("encounters.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=False,
        index=True,
    )

    # Note Details
    note_type: Mapped[NoteType] = mapped_column(
        SQLEnum(NoteType),
        default=NoteType.SOAP,
        nullable=False,
    )

    # Content (structured based on note_type)
    # For SOAP: { "subjective": "...", "objective": "...", "assessment": "...", "plan": "..." }
    content: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Additional text content
    narrative: Mapped[str | None] = mapped_column(Text())

    # Status
    is_draft: Mapped[bool] = mapped_column(default=True, nullable=False)
    is_signed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Signing
    signed_at: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))  # Should be DateTime
    signed_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))

    # AI Assistance
    is_ai_generated: Mapped[bool] = mapped_column(default=False)
    ai_confidence: Mapped[float | None] = mapped_column(default=None)

    # Relationships
    encounter = relationship("Encounter", back_populates="notes")
    author = relationship("User", foreign_keys=[author_id], back_populates="authored_notes")

    def __repr__(self) -> str:
        return f"<Note(id={self.id}, type='{self.note_type}', signed={self.is_signed})>"
