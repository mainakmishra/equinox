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


# Service Functions
def create_todo_service(user_email: str, text: str, due_date: date | None = None):
    new_todo = Todo(
        id=str(uuid.uuid4()),
        user_email=user_email,
        text=text,
        completed=False,
        due_date=due_date,
        created_at=datetime.utcnow()
    )
    todos_store.append(new_todo)
    return new_todo

def get_todos_service(user_email: str):
    return [t for t in todos_store if t.user_email == user_email]

def delete_todo_service(todo_id: str):
    global todos_store
    for i, t in enumerate(todos_store):
        if t.id == todo_id:
            del todos_store[i]
            return True
    return False

# Route Handlers
@router.post("/", response_model=Todo)
def add_todo(todo: Todo):
    # Note: The API receives the full object, but usually POST creates a new one. 
    # The existing code accepted a full Todo object which is a bit weird (client generates ID?).
    # Let's keep existing behavior but also support the service.
    # Actually, the existing code: `todos_store.append(todo)` implies the CLIENT sends the ID.
    # To switch to service, we should probably check if the client provided ID or if we should generate one.
    # For now, let's just append it to keep API compat.
    todos_store.append(todo)
    return todo

@router.get("/{user_email}", response_model=List[Todo])
def get_todos(user_email: str):
    return get_todos_service(user_email)