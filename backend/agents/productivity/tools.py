
# productivity agent tools

from langchain_core.tools import tool
from typing import Optional, List
from datetime import datetime
import uuid

# Import database dependencies
from database import SessionLocal

# Import Services
from api.notes import (
    create_note_service, 
    get_user_notes_service, 
    delete_note_service
)
from api.todos import (
    create_todo_service, 
    get_todos_service, 
    delete_todo_service
)

from tools import google_auth


@tool
def fetch_recent_emails(user_id: str) -> dict:
    """
    Fetch recent emails from Gmail.
    Useful for summarizing work or checking for missed messages.
    """
    from state.user_tokens import get_user_tokens
    
    tokens = get_user_tokens(user_id)
    if not tokens:
        return {"error": "No Google tokens found. User needs to sign in."}
        
    service = google_auth.get_gmail_service(tokens)
    emails = google_auth.fetch_recent_emails(service)
    return {"recent_emails": emails}

# Notes Tools

@tool
def fetch_notes(user_email: str) -> dict:
    """
    Fetch all notes for a specific user.
    """
    session = SessionLocal()
    try:
        notes = get_user_notes_service(session, user_email)
        # Serialize
        notes_list = [
            {
                "id": str(n.id),
                "title": n.title,
                "content": n.content,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notes
        ]
        return {"notes": notes_list}
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

@tool
def create_note(user_email: str, title: str, content: str) -> dict:
    """
    Create a new note for the user. 
    """
    session = SessionLocal()
    try:
        new_note = create_note_service(session, user_email, title, content, source='ai_agent')
        return {
            "status": "success", 
            "note_id": str(new_note.id), 
            "message": f"Note '{title}' created."
        }
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

@tool
def delete_note(note_id: str) -> dict:
    """
    Delete a note by its ID.
    """
    session = SessionLocal()
    try:
        # Validate UUID
        try:
            n_uuid = uuid.UUID(note_id)
        except ValueError:
            return {"error": "Invalid Note ID format."}

        success = delete_note_service(session, n_uuid)
        if success:
             return {"status": "success", "message": "Note deleted."}
        else:
             return {"error": "Note not found."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        session.close()

# Todos Tools

@tool
def fetch_todos(user_email: str) -> dict:
    """
    Fetch all todos for a specific user.
    """
    todos = get_todos_service(user_email)
    return {"todos": [t.dict() for t in todos]}

@tool
def create_todo(user_email: str, text: str, due_date: Optional[str] = None) -> dict:
    """
    Create a new todo item.
    """
    try:
        parsed_date = None
        if due_date:
            try:
                parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD."}

        new_todo = create_todo_service(user_email, text, parsed_date)
        return {"status": "success", "todo_id": new_todo.id, "message": f"Todo '{text}' created."}
    except Exception as e:
        return {"error": str(e)}

@tool
def delete_todo(todo_id: str) -> dict:
    """
    Delete a todo by its ID.
    """
    success = delete_todo_service(todo_id)
    if success:
        return {"status": "success", "message": "Todo deleted."}
    else:
        return {"error": "Todo not found."}


PRODUCTIVITY_TOOLS = [fetch_recent_emails, fetch_notes, create_note, delete_note, fetch_todos, create_todo, delete_todo]

