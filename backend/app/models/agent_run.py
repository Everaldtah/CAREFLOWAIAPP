"""
Agent Run Model

Tracks execution of AI agents for audit and learning.
"""

import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID

from app.core.base import BaseModel


class AgentStatus(str, Enum):
    """Agent execution status."""
    STARTED = "started"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AgentRun(BaseModel):
    """
    AI agent execution record.

    Tracks each agent run for debugging, auditing, and improvement.
    """

    # Foreign Keys
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Agent Details
    agent_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    agent_version: Mapped[str] = mapped_column(String(50), default="1.0")
    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(AgentStatus),
        default=AgentStatus.STARTED,
        nullable=False,
    )

    # Execution
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    duration_ms: Mapped[int | None] = mapped_column(default=None)

    # Input/Output
    input_data: Mapped[dict | None] = mapped_column(JSON, default=dict)
    output_data: Mapped[dict | None] = mapped_column(JSON, default=dict)

    # Model Details
    model_name: Mapped[str | None] = mapped_column(String(100))
    model_version: Mapped[str | None] = mapped_column(String(50))
    tokens_input: Mapped[int | None] = mapped_column(default=None)
    tokens_output: Mapped[int | None] = mapped_column(default=None)
    total_cost: Mapped[float | None] = mapped_column(default=None)

    # Error Handling
    error_message: Mapped[str | None] = mapped_column(Text())
    error_details: Mapped[dict | None] = mapped_column(JSON)

    # Human Feedback
    user_feedback: Mapped[str | None] = mapped_column(String(20))  # 'positive', 'negative', 'neutral'
    feedback_notes: Mapped[str | None] = mapped_column(Text())

    # Context
    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    clinic_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)

    def __repr__(self) -> str:
        return f"<AgentRun(id={self.id}, agent='{self.agent_type}', status='{self.status}')>"
