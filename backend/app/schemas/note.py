from enum import Enum
"""
Note Schemas
"""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel


class NoteType(str, Enum):
    """Note types."""
    SOAP = "soap"
    PROGRESS = "progress_note"
    CONSULTATION = "consultation"
    PROCEDURE = "procedure_note"
    DISCHARGE = "discharge_summary"
    TELEPHONE = "telephone_note"
    EMAIL = "email_note"
    OTHER = "other"


class SOAPNoteData(BaseModel):
    """SOAP note structure."""
    subjective: Optional[str] = None
    objective: Optional[str] = None
    assessment: Optional[str] = None
    plan: Optional[str] = None

    def dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "subjective": self.subjective,
            "objective": self.objective,
            "assessment": self.assessment,
            "plan": self.plan,
        }


class NoteCreate(BaseModel):
    """Request schema for creating a note."""
    encounter_id: UUID
    note_type: NoteType = NoteType.SOAP
    content: dict  # Structured content based on note_type
    narrative: Optional[str] = None


class NoteUpdate(BaseModel):
    """Request schema for updating a note."""
    content: Optional[dict] = None
    narrative: Optional[str] = None


class NoteResponse(BaseModel):
    """Response schema for note."""
    id: UUID
    encounter_id: UUID
    author_id: UUID
    note_type: str
    content: dict
    narrative: Optional[str]
    is_draft: bool
    is_signed: bool
    is_ai_generated: bool
    ai_confidence: Optional[float]
    created_at: datetime
    updated_at: datetime


class NoteListResponse(BaseModel):
    """Response schema for note list."""
    items: list[NoteResponse]
    total: int
    skip: int
    limit: int
