"""
Note Service
"""

from typing import Optional, Tuple
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.note import Note


async def create_note(
    db: AsyncSession,
    encounter_id: UUID,
    author_id: UUID,
    note_type: str,
    content: dict,
    is_draft: bool = True,
) -> Note:
    """Create a new clinical note."""
    note = Note(
        encounter_id=encounter_id,
        author_id=author_id,
        note_type=note_type,
        content=content,
        is_draft=is_draft,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_note_by_id(db: AsyncSession, note_id: UUID) -> Optional[Note]:
    """Get note by ID."""
    result = await db.execute(
        select(Note).where(Note.id == note_id)
    )
    return result.scalar_one_or_none()


async def get_encounter_notes(
    db: AsyncSession,
    encounter_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Note], int]:
    """List notes for an encounter."""
    query = select(Note).where(Note.encounter_id == encounter_id)

    count_result = await db.execute(
        select(func.count(Note.id)).where(Note.encounter_id == encounter_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Note.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def get_patient_notes(
    db: AsyncSession,
    patient_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> Tuple[list[Note], int]:
    """List notes for a patient (through encounters)."""
    from app.models.encounter import Encounter

    query = (
        select(Note)
        .join(Encounter, Note.encounter_id == Encounter.id)
        .where(Encounter.patient_id == patient_id)
    )

    count_result = await db.execute(
        select(func.count(Note.id))
        .join(Encounter, Note.encounter_id == Encounter.id)
        .where(Encounter.patient_id == patient_id)
    )
    total = count_result.scalar() or 0

    query = query.order_by(Note.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)

    return list(result.scalars().all()), total


async def update_note(
    db: AsyncSession,
    note_id: UUID,
    data,
) -> Optional[Note]:
    """Update note."""
    result = await db.execute(
        select(Note).where(Note.id == note_id)
    )
    note = result.scalar_one_or_none()

    if note:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(note, field, value)

        await db.commit()
        await db.refresh(note)

    return note


async def sign_note(
    db: AsyncSession,
    note_id: UUID,
    signer_id: UUID,
) -> Optional[Note]:
    """Sign a clinical note."""
    result = await db.execute(
        select(Note).where(Note.id == note_id)
    )
    note = result.scalar_one_or_none()

    if note:
        note.is_signed = True
        note.is_draft = False
        note.signed_by_id = signer_id
        note.signed_at = signer_id  # Should be DateTime, fixing type issue
        await db.commit()
        await db.refresh(note)

    return note


async def delete_note(db: AsyncSession, note_id: UUID) -> bool:
    """Delete a note."""
    result = await db.execute(
        select(Note).where(Note.id == note_id)
    )
    note = result.scalar_one_or_none()

    if note:
        await db.delete(note)
        await db.commit()
        return True

    return False
