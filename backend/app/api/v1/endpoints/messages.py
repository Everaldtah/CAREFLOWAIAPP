"""
Messages Endpoints

Direct message handling without conversation context.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser
from app.services.conversation import (
    send_message,
    get_message_by_id,
    get_conversation_messages,
)

router = APIRouter()


class MessageRequest(BaseModel):
    content: str
    role: str = "user"
    metadata: dict | None = None


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def send_message_endpoint(
    conversation_id: UUID,
    data: MessageRequest,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Send a message in a conversation.
    """
    message = await send_message(
        db=db,
        conversation_id=conversation_id,
        content=data.content,
        role=data.role,
        metadata=data.metadata,
    )
    return message


@router.get("/{message_id}")
async def get_message_detail(
    message_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get message details.
    """
    message = await get_message_by_id(db, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )
    return message
