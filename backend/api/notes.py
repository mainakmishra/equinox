# routers/notes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from database.models import Note
from schemas.notes import NoteCreate, NoteUpdate, NoteResponse

router = APIRouter(prefix="/notes", tags=["notes"])



# Service Functions (for Agent Use)
def create_note_service(db: Session, user_email: str, title: str, content: str, source: str = "user"):
    note = Note(
        user_email=user_email,
        title=title,
        content=content,
        source=source
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

def get_user_notes_service(db: Session, user_email: str):
    return db.query(Note)\
        .filter(Note.user_email == user_email)\
        .order_by(Note.created_at.desc())\
        .all()

def get_note_service(db: Session, note_id: UUID):
    return db.query(Note).filter(Note.id == note_id).first()

def update_note_service(db: Session, note_id: UUID, title: str | None = None, content: str | None = None):
    note = get_note_service(db, note_id)
    if not note:
        return None
    
    if title is not None:
        note.title = title
    if content is not None:
        note.content = content
    
    db.commit()
    db.refresh(note)
    return note

def delete_note_service(db: Session, note_id: UUID):
    note = get_note_service(db, note_id)
    if not note:
        return False
    
    db.delete(note)
    db.commit()
    return True

# Route Handlers
@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(note_data: NoteCreate, db: Session = Depends(get_db)):
    """Create a new note"""
    return create_note_service(
        db, 
        note_data.user_email, 
        note_data.title, 
        note_data.content, 
        note_data.source
    )


@router.get("/{user_email}", response_model=List[NoteResponse])
def get_user_notes(user_email: str, db: Session = Depends(get_db)):
    """Get all notes for a user, ordered by most recent first"""
    return get_user_notes_service(db, user_email)


@router.get("/note/{note_id}", response_model=NoteResponse)
def get_note(note_id: UUID, db: Session = Depends(get_db)):
    """Get a specific note by ID"""
    note = get_note_service(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(note_id: UUID, update_data: NoteUpdate, db: Session = Depends(get_db)):
    """Update a note's title and/or content"""
    note = update_note_service(db, note_id, update_data.title, update_data.content)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.delete("/{note_id}", status_code=204)
def delete_note(note_id: UUID, db: Session = Depends(get_db)):
    """Delete a note"""
    success = delete_note_service(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Note not found")
    return None