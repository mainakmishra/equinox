from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Todo as TodoModel

from state.user_tokens import get_user_tokens
from tools.google_auth import get_tasks_service, fetch_tasks

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
    # 1. Fetch Local Todos
    local_todos = db.query(TodoModel).filter(TodoModel.user_email == user_email).order_by(TodoModel.created_at.desc()).all()
    
    # Convert to response model format immediately to allow merging
    response_todos = []
    for t in local_todos:
        response_todos.append(TodoResponse(
            id=str(t.id),
            user_email=t.user_email,
            text=t.text,
            completed=t.completed,
            due_date=t.due_date,
            created_at=t.created_at
        ))

    # 2. Fetch Google Tasks
    try:
        tokens = get_user_tokens(user_email)
        if tokens:
            service = get_tasks_service(tokens)
            # Fetch from default list
            google_tasks = fetch_tasks(service, '@default')
            
            for g_task in google_tasks:
                # Map Google Task to TodoResponse
                # Google Task structure: {'id': '...', 'title': '...', 'status': 'needsAction'|'completed', 'due': '...'}
                is_completed = g_task.get('status') == 'completed'
                due = None
                if g_task.get('due'):
                    try:
                        # RFC 3339 timestamp to date
                        due = datetime.fromisoformat(g_task['due'].replace('Z', '+00:00')).date()
                    except:
                        pass
                
                # Determine creation time (Google doesn't explicitly give created_at in simple list, use updated or now)
                # For sorting, we can use 'updated' if available
                created_at = datetime.now()
                if g_task.get('updated'):
                    try:
                         created_at = datetime.fromisoformat(g_task['updated'].replace('Z', '+00:00'))
                    except:
                        pass

                response_todos.append(TodoResponse(
                    id=g_task.get('id'), # Use Google ID directly
                    user_email=user_email,
                    text=g_task.get('title', '(No Title)'),
                    completed=is_completed,
                    due_date=due,
                    created_at=created_at
                ))
    except Exception as e:
        print(f"Error fetching Google Tasks for {user_email}: {e}")
        # Validate/Refresh tokens logic might be needed here in production, 
        # but for now we just fail gracefully and show local todos.

    # 3. Sort combined list by created_at desc
    response_todos.sort(key=lambda x: x.created_at, reverse=True)
    
    return response_todos

def delete_todo_service(db: Session, todo_id_str: str):
    try:
        todo_uuid = uuid.UUID(todo_id_str)
    except ValueError:
        # If it's not a UUID, it might be a Google Task ID
        # We currently don't implement deleting Google Tasks via this endpoint
        # The user would need to use a specific google task delete endpoint or we handle it here
        # For this iteration, we return False for non-UUIDs (Google IDs)
        # TODO: Implement Google Task deletion
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
        # TODO: Implement Google Task update
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
    # TODO: Add to Google Tasks if user is authenticated?
    # For now, add to local DB
    return create_todo_service(db, todo.user_email, todo.text, todo.due_date)

@router.get("/{user_email}", response_model=List[TodoResponse])
def get_todos(user_email: str, db: Session = Depends(get_db)):
    return get_todos_service(db, user_email)

@router.delete("/{todo_id}")
def delete_todo(todo_id: str, user_email: Optional[str] = None, db: Session = Depends(get_db)):
    # Try local delete first
    success = delete_todo_service(db, todo_id)
    if success:
        return {"message": "Todo deleted successfully"}
        
    # If fetch failed or wasn't a UUID, try Google Task
    if user_email:
        from tools.google_auth import get_tasks_service, delete_task
        tokens = get_user_tokens(user_email)
        if tokens:
            try:
                service = get_tasks_service(tokens)
                delete_task(service, todo_id)
                return {"message": "Google Task deleted successfully"}
            except Exception as e:
                print(f"Failed to delete Google Task: {e}")
                
    raise HTTPException(status_code=404, detail="Todo not found (or failed to delete Google Task)")

@router.put("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, updates: TodoUpdate, user_email: Optional[str] = None, db: Session = Depends(get_db)):
    # Try local update first
    updated_todo = update_todo_service(db, todo_id, updates)
    if updated_todo:
        return updated_todo
        
    # Try Google Task update
    if user_email:
        from tools.google_auth import get_tasks_service, update_task
        tokens = get_user_tokens(user_email)
        if tokens:
            try:
                service = get_tasks_service(tokens)
                
                status = None
                if updates.completed is not None:
                    status = 'completed' if updates.completed else 'needsAction'
                
                due = None
                if updates.due_date:
                    # Convert date to RFC 3339 string (e.g. 2023-10-01T00:00:00.000Z)
                    due = f"{updates.due_date.isoformat()}T00:00:00.000Z"
                
                g_task = update_task(service, todo_id, title=updates.text, status=status, due=due)
                
                # Convert back to response model
                is_completed = g_task.get('status') == 'completed'
                
                return TodoResponse(
                    id=g_task.get('id'),
                    user_email=user_email,
                    text=g_task.get('title'),
                    completed=is_completed,
                    due_date=updates.due_date, # Use passed due date as approximation or parse from response
                    created_at=datetime.now() # Mock
                )
            except Exception as e:
                print(f"Failed to update Google Task: {e}")

    raise HTTPException(status_code=404, detail="Todo not found (or failed to update Google Task)")