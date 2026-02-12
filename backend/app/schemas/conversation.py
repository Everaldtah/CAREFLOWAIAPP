from enum import Enum
"""
Conversation Schemas
"""

from datetime import datetime
from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel


class AgentType(str, Enum):
    """AI agent types."""
    TRIAGE = "triage"
    SCHEDULING = "scheduling"
    SCRIBE = "scribe"
    FOLLOW_UP = "follow_up"
    BILLING = "billing"
    GENERAL = "general"


class ConversationCreate(BaseModel):
    """Request schema for creating a conversation."""
    agent_type: AgentType = AgentType.GENERAL
    patient_id: Optional[UUID] = None
    context: Optional[dict] = None


class ConversationResponse(BaseModel):
    """Response schema for conversation."""
    id: UUID
    user_id: UUID
    patient_id: Optional[UUID]
    agent_type: str
    status: str
    topic: Optional[str]
    context: Optional[dict]
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    """Response schema for conversation list."""
    items: list[ConversationResponse]
    total: int


class MessageResponse(BaseModel):
    """Response schema for message."""
    id: UUID
    conversation_id: UUID
    role: str
    content: str
    metadata: Optional[dict]
    model: Optional[str]
    tokens_used: Optional[int]
    confidence: Optional[float]
    created_at: datetime


class AgentResponse(BaseModel):
    """Response schema for AI agent."""
    content: str
    metadata: Optional[dict] = None
    confidence: Optional[float] = None
    escalated: bool = False
