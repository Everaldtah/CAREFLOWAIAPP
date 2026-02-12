"""
Clinical Notes Endpoints

Handles clinical documentation including SOAP notes.
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import ActiveUser, require_provider, Pagination
from app.schemas.note import (
    NoteCreate,
    NoteUpdate,
    NoteResponse,
    NoteListResponse,
    SOAPNoteData,
)
from app.services.note import (
    create_note,
    get_note_by_id,
    get_encounter_notes,
    get_patient_notes,
    update_note,
    delete_note,
    sign_note,
)
from app.agents.scribe_agent import ScribeAgent
from app.services.audit import log_phi_access

router = APIRouter()


class GenerateNoteRequest(BaseModel):
    encounter_id: UUID
    transcript: str | None = None
    recording_url: str | None = None
    note_type: str = "soap"


@router.post("/", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note_endpoint(
    data: NoteCreate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Create a new clinical note.

    - Can be SOAP or other format
    - Links to encounter
    - Draft status until signed
    """
    note = await create_note(
        db=db,
        encounter_id=data.encounter_id,
        author_id=current_user.id,
        note_type=data.note_type,
        content=data.content,
    )

    # Log PHI access
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="note",
        resource_id=note.id,
        action="create",
    )

    return note


@router.post("/generate", response_model=NoteResponse)
async def generate_ai_note(
    data: GenerateNoteRequest,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Generate clinical note using AI scribe.

    - Processes transcript or recording
    - Structures into SOAP format
    - Creates draft note for review
    """
    scribe = ScribeAgent(db)

    try:
        # Generate SOAP note from transcript
        soap_data = await scribe.transcribe_to_soap(
            encounter_id=data.encounter_id,
            transcript=data.transcript,
        )

        # Create note with generated content
        note = await create_note(
            db=db,
            encounter_id=data.encounter_id,
            author_id=current_user.id,
            note_type=data.note_type,
            content=soap_data.dict(),
            is_draft=True,
        )

        # Log AI generation
        await log_phi_access(
            db=db,
            user_id=current_user.id,
            resource_type="note",
            resource_id=note.id,
            action="ai_generate",
        )

        return note

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate note: {str(e)}",
        )


@router.get("/", response_model=NoteListResponse)
async def list_notes(
    current_user: ActiveUser,
    pagination: Pagination,
    db: AsyncSession = Depends(get_async_db),
    encounter_id: UUID | None = Query(None),
    patient_id: UUID | None = Query(None),
    is_draft: bool | None = Query(None),
) -> Any:
    """
    List clinical notes.

    - Filter by encounter or patient
    - Filter by draft status
    - Paginated results
    """
    if encounter_id:
        notes, total = await get_encounter_notes(
            db=db,
            encounter_id=encounter_id,
            skip=pagination.skip,
            limit=pagination.limit,
        )
    elif patient_id:
        notes, total = await get_patient_notes(
            db=db,
            patient_id=patient_id,
            skip=pagination.skip,
            limit=pagination.limit,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify encounter_id or patient_id",
        )

    # Filter by draft status if specified
    if is_draft is not None:
        notes = [n for n in notes if n.is_draft == is_draft]
        total = len(notes)

    return NoteListResponse(
        items=notes,
        total=total,
        skip=pagination.skip,
        limit=pagination.limit,
    )


@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(
    note_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Get note details.
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Verify clinic access
    from app.services.encounter import get_encounter_by_id
    encounter = await get_encounter_by_id(db, note.encounter_id)
    if encounter.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    return note


@router.patch("/{note_id}", response_model=NoteResponse)
async def update_note_endpoint(
    note_id: UUID,
    data: NoteUpdate,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Update clinical note.

    - Can edit content
    - Cannot edit signed notes
    - Logs PHI modifications
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Check if signed
    if note.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot edit signed notes",
        )

    # Verify access
    from app.services.encounter import get_encounter_by_id
    encounter = await get_encounter_by_id(db, note.encounter_id)
    if encounter.clinic_id != current_user.clinic_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied",
        )

    updated = await update_note(db, note_id, data)

    # Log modification
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="note",
        resource_id=note_id,
        action="update",
    )

    return updated


@router.post("/{note_id}/sign", response_model=NoteResponse)
async def sign_note_endpoint(
    note_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> Any:
    """
    Sign a clinical note.

    - Marks note as signed
    - Cannot be edited after signing
    - Records signature timestamp
    - Provider must be note author
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    # Verify author
    if note.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the note author can sign it",
        )

    signed = await sign_note(db, note_id, current_user.id)

    # Log signing
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="note",
        resource_id=note_id,
        action="sign",
    )

    return signed


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_endpoint(
    note_id: UUID,
    current_user: ActiveUser,
    db: AsyncSession = Depends(get_async_db),
) -> None:
    """
    Delete a clinical note.

    - Can only delete unsigned notes
    - Soft delete for audit trail
    """
    note = await get_note_by_id(db, note_id)
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )

    if note.is_signed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete signed notes",
        )

    await delete_note(db, note_id)

    # Log deletion
    await log_phi_access(
        db=db,
        user_id=current_user.id,
        resource_type="note",
        resource_id=note_id,
        action="delete",
    )
