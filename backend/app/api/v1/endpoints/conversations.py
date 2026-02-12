"""
AI Conversation Endpoints

Handles AI agent interactions for triage, scheduling, and patient communication.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser
from app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationListResponse,
    MessageCreate,
    MessageResponse,
    AgentResponse,
)
from app.services.conversation import (
    create_conversation,
    get_conversation_by_id,
    get_user_conversations,
    send_message,
    trigger_agent_response,
    get_conversation_messages,
    escalate_to_human,
)
from app.agents.orchestrator import AgentOrchestrator
from app.services.audit import log_phi_access

router = APIRouter()


class SendMessageRequest(BaseModel):
    message: str
    agent_type: str | None = None  # 'triage', 'scheduling', 'general'


@router.post("/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def create_new_conversation(
    data: ConversationCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create a new conversation with an AI agent.

    - Initializes conversation context
    - Sets up agent type
    - Can be patient-initiated or staff-initiated
    """
    conversation = await create_conversation(
        db=db,
        user_id=current_user.id,
        agent_type=data.agent_type,
        patient_id=data.patient_id,
        context=data.context,
    )

    return conversation


@router.get("/", response_model=ConversationListResponse)
async def list_conversations(
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
    active_only: bool = False,
) -> Any:
    """
    List user's conversations.

    - Can filter by active status
    - Ordered by most recent
    """
    conversations = await get_user_conversations(
        db=db,
        user_id=current_user.id,
        active_only=active_only,
    )

    return ConversationListResponse(
        items=conversations,
        total=len(conversations),
    )


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get conversation details with message history.
    """
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Verify access
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Log PHI access if patient-related
    if conversation.patient_id:
        await log_phi_access(
            db=db,
            user_id=current_user.id,
            resource_type="conversation",
            resource_id=conversation_id,
            action="read",
        )

    return conversation


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    conversation_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get all messages in a conversation.
    """
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    messages = await get_conversation_messages(db, conversation_id)
    return messages


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def send_user_message(
    conversation_id: UUID,
    data: SendMessageRequest,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Send a message in a conversation and get AI response.

    - Processes user message
    - Triggers appropriate AI agent
    - Returns agent response
    - Handles escalations
    """
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    # Create user message
    user_message = await send_message(
        db=db,
        conversation_id=conversation_id,
        content=data.message,
        role="user",
    )

    # Trigger AI response
    try:
        orchestrator = AgentOrchestrator(db)
        agent_response = await orchestrator.process_message(
            conversation_id=conversation_id,
            message=data.message,
            agent_type=data.agent_type or conversation.agent_type,
            user_id=current_user.id,
        )

        # Create assistant message
        assistant_message = await send_message(
            db=db,
            conversation_id=conversation_id,
            content=agent_response["content"],
            role="assistant",
            metadata=agent_response.get("metadata", {}),
        )

        # Log PHI access
        if conversation.patient_id:
            await log_phi_access(
                db=db,
                user_id=current_user.id,
                resource_type="conversation",
                resource_id=conversation_id,
                action="message",
            )

        return assistant_message

    except Exception as e:
        # Handle agent errors
        error_message = await send_message(
            db=db,
            conversation_id=conversation_id,
            content=f"I apologize, but I encountered an error: {str(e)}",
            role="assistant",
            metadata={"error": True},
        )
        return error_message


@router.post("/{conversation_id}/escalate")
async def escalate_conversation(
    conversation_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Escalate conversation to human staff.

    - Flags conversation for human review
    - Sends notification to staff
    - Pauses automated responses
    """
    conversation = await get_conversation_by_id(db, conversation_id)
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    await escalate_to_human(
        db=db,
        conversation_id=conversation_id,
        reason="User requested escalation",
    )

    return {"message": "Conversation escalated to staff"}


@router.post("/{conversation_id}/resolve")
async def resolve_conversation(
    conversation_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Mark conversation as resolved.

    - Closes conversation
    - Updates agent learning
    """
    from app.services.conversation import close_conversation

    await close_conversation(db, conversation_id)

    return {"message": "Conversation resolved"}


@router.post("/triage", response_model=AgentResponse)
async def initiate_triage(
    patient_id: UUID,
    symptoms: str,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Initiate AI triage for a patient.

    - Assess symptom urgency
    - Recommend action (ER, urgent care, schedule, home care)
    - Document triage decision
    """
    from app.agents.triage_agent import TriageAgent

    triage_agent = TriageAgent(db)
    result = await triage_agent.assess(
        patient_id=patient_id,
        symptoms=symptoms,
    )

    # Log PHI access
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="triage",
        resource_id=patient_id,
        action="assess",
    )

    return result


@router.post("/scheduling/suggest")
async def get_scheduling_suggestions(
    patient_id: UUID,
    appointment_type: str,
    duration_minutes: int,
    preferred_dates: List[str],
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get AI-powered scheduling suggestions.

    - Finds optimal time slots
    - Considers provider availability
    - Minimizes gaps
    """
    from app.agents.scheduling_agent import SchedulingAgent

    scheduler = SchedulingAgent(db)
    suggestions = await scheduler.suggest_slots(
        clinic_id=current_user.clinic_id,
        patient_id=patient_id,
        appointment_type=appointment_type,
        duration_minutes=duration_minutes,
        preferred_dates=preferred_dates,
    )

    return {"suggestions": suggestions}
