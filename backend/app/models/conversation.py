"""
Conversation and Message Models

AI agent conversation tracking.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class AgentType(str, Enum):
    """Types of AI agents."""
    TRIAGE = "triage"  # Symptom assessment
    SCHEDULING = "scheduling"  # Appointment booking
    SCRIBE = "scribe"  # Clinical documentation
    FOLLOW_UP = "follow_up"  # Patient follow-up
    BILLING = "billing"  # Billing questions
    GENERAL = "general"  # General assistance


class ConversationStatus(str, Enum):
    """Conversation status."""
    ACTIVE = "active"
    PAUSED = "paused"
    ESCALATED = "escalated_to_human"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Conversation(BaseModel):
    """
    AI conversation model.

    Tracks multi-turn conversations with AI agents.
    """

    # Foreign Keys
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    patient_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patients.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Conversation Details
    agent_type: Mapped[AgentType] = mapped_column(
        SQLEnum(AgentType),
        default=AgentType.GENERAL,
        nullable=False,
        index=True,
    )
    status: Mapped[ConversationStatus] = mapped_column(
        SQLEnum(ConversationStatus),
        default=ConversationStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    # Context
    topic: Mapped[str | None] = mapped_column(String(255))
    context: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Escalation
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    escalated_to_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))  # Staff user ID

    # Resolution
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    resolution: Mapped[str | None] = mapped_column(Text())

    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    @property
    def message_count(self) -> int:
        """Get number of messages in conversation."""
        return len(self.messages)

    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, agent='{self.agent_type}', status='{self.status}')>"


class MessageRole(str, Enum):
    """Message roles."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Message(BaseModel):
    """
    Message model within conversations.

    Represents individual messages in an AI conversation.
    """

    # Foreign Keys
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Message Content
    role: Mapped[MessageRole] = mapped_column(
        SQLEnum(MessageRole),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text(), nullable=False)

    # Extra metadata (tokens, model used, etc.)
    extra_metadata: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # AI Response Details
    model: Mapped[str | None] = mapped_column(String(100))  # LLM model used
    tokens_used: Mapped[int | None] = mapped_column(default=None)
    confidence: Mapped[float | None] = mapped_column(default=None)

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role='{self.role}', content='{self.content[:50]}...')>"
