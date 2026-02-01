# routers/notes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from database.models import Note
from schemas.notes import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    note = Note(
        user_email=note_data.user_email,
        title=note_data.title,
        content=note_data.content,
        source=note_data.source
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{user_email}", response_model=List[NoteResponse])
def get_user_notes(user_email: str, db: Session = Depends(get_db)):
    """Get all notes for a user, ordered by most recent first"""
    notes = db.query(Note)\
        .filter(Note.user_email == user_email)\
        .order_by(Note.created_at.desc())\
        .all()
    return notes


@router.get("/note/{note_id}", response_model=NoteResponse)
def get_note(note_id: UUID, db: Session = Depends(get_db)):
    """Get a specific note by ID"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(note_id: UUID, update_data: NoteUpdate, db: Session = Depends(get_db)):
    """Update a note's title and/or content"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Update only provided fields
    if update_data.title is not None:
        note.title = update_data.title
    if update_data.content is not None:
        note.content = update_data.content
    
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: UUID, db: Session = Depends(get_db)):
    """Delete a note"""
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    db.delete(note)
    db.commit()
    return None