"""
Conversation Service
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation, Message, ConversationStatus


async def create_conversation(
    db: AsyncSession,
    user_id: UUID,
    agent_type: str,
    patient_id: Optional[UUID] = None,
    context: Optional[dict] = None,
) -> Conversation:
    """Create a new conversation."""
    conversation = Conversation(
        user_id=user_id,
        agent_type=agent_type,
        patient_id=patient_id,
        context=context,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    return conversation


async def get_conversation_by_id(
    db: AsyncSession,
    conversation_id: UUID,
) -> Optional[Conversation]:
    """Get conversation by ID."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    return result.scalar_one_or_none()


async def get_user_conversations(
    db: AsyncSession,
    user_id: UUID,
    active_only: bool = False,
) -> List[Conversation]:
    """List conversations for a user."""
    query = select(Conversation).where(Conversation.user_id == user_id)

    if active_only:
        query = query.where(Conversation.status == ConversationStatus.ACTIVE)

    query = query.order_by(Conversation.created_at.desc())

    result = await db.execute(query)
    return list(result.scalars().all())


async def send_message(
    db: AsyncSession,
    conversation_id: UUID,
    content: str,
    role: str,
    metadata: Optional[dict] = None,
) -> Message:
    """Send a message in a conversation."""
    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content,
        metadata=metadata or {},
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


async def get_message_by_id(
    db: AsyncSession,
    message_id: UUID,
) -> Optional[Message]:
    """Get message by ID."""
    result = await db.execute(
        select(Message).where(Message.id == message_id)
    )
    return result.scalar_one_or_none()


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: UUID,
) -> List[Message]:
    """Get all messages in a conversation."""
    result = await db.execute(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def escalate_to_human(
    db: AsyncSession,
    conversation_id: UUID,
    reason: str,
) -> Conversation:
    """Escalate conversation to human staff."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        conversation.status = ConversationStatus.ESCALATED
        conversation.escalated_at = datetime.utcnow()
        await db.commit()
        await db.refresh(conversation)

    return conversation


async def close_conversation(
    db: AsyncSession,
    conversation_id: UUID,
) -> Conversation:
    """Close a conversation."""
    result = await db.execute(
        select(Conversation).where(Conversation.id == conversation_id)
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        conversation.status = ConversationStatus.CLOSED
        conversation.resolved_at = datetime.utcnow()
        await db.commit()
        await db.refresh(conversation)

    return conversation
