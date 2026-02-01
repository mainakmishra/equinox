from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import uuid

router = APIRouter(prefix="/todos", tags=["todos"])
todos_store = []

class Todo(BaseModel):
    id: str
    user_email: str
    text: str
    completed: bool = False
    due_date: Optional[date] = None
    created_at: datetime

@router.post("/", response_model=Todo)
def add_todo(todo: Todo):
    todos_store.append(todo)
    return todo

@router.get("/{user_email}", response_model=List[Todo])
def get_todos(user_email: str):
    return [t for t in todos_store if t.user_email == user_email]