from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Todo as TodoModel

router = APIRouter(prefix="/todos", tags=["todos"])

class TodoCreate(BaseModel):
    user_email: str
    text: str
    due_date: Optional[date] = None

class TodoUpdate(BaseModel):
    text: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[date] = None

class TodoResponse(BaseModel):
    id: str
    user_email: str
    text: str
    completed: bool
    due_date: Optional[date]
    created_at: datetime
    
    class Config:
        orm_mode = True

# Service Functions
def create_todo_service(db: Session, user_email: str, text: str, due_date: Optional[date] = None):
    db_todo = TodoModel(
        user_email=user_email,
        text=text,
        due_date=due_date
    )
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    # Cast uuid to string
    db_todo.id = str(db_todo.id)
    return db_todo

def get_todos_service(db: Session, user_email: str):
    todos = db.query(TodoModel).filter(TodoModel.user_email == user_email).order_by(TodoModel.created_at.desc()).all()
    # Cast uuid to string
    for t in todos:
        t.id = str(t.id)
    return todos

def delete_todo_service(db: Session, todo_id_str: str):
    try:
        todo_uuid = uuid.UUID(todo_id_str)
    except ValueError:
        return False
        
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_uuid).first()
    if not db_todo:
        return False
    
    db.delete(db_todo)
    db.commit()
    return True

def update_todo_service(db: Session, todo_id_str: str, updates: TodoUpdate):
    try:
        todo_uuid = uuid.UUID(todo_id_str)
    except ValueError:
        return None
        
    db_todo = db.query(TodoModel).filter(TodoModel.id == todo_uuid).first()
    if not db_todo:
        return None
    
    if updates.text is not None:
        db_todo.text = updates.text
    if updates.completed is not None:
        db_todo.completed = updates.completed
    if updates.due_date is not None:
        db_todo.due_date = updates.due_date
        
    db.commit()
    db.refresh(db_todo)
    db_todo.id = str(db_todo.id)
    return db_todo

# Route Handlers

@router.post("/", response_model=TodoResponse)
def add_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    return create_todo_service(db, todo.user_email, todo.text, todo.due_date)

@router.get("/{user_email}", response_model=List[TodoResponse])
def get_todos(user_email: str, db: Session = Depends(get_db)):
    return get_todos_service(db, user_email)

@router.delete("/{todo_id}")
def delete_todo(todo_id: str, db: Session = Depends(get_db)):
    success = delete_todo_service(db, todo_id)
    if not success:
         raise HTTPException(status_code=404, detail="Todo not found or invalid ID")
    return {"message": "Todo deleted successfully"}

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, updates: TodoUpdate, db: Session = Depends(get_db)):
    updated_todo = update_todo_service(db, todo_id, updates)
    if not updated_todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated_todo