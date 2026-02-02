# productivity agent tools

from langchain_core.tools import tool
from typing import Optional, List
# from .productivity_tools import ProductivityAgent # Removed to avoid ImportError since we reimplement/mock logic here


# We'll use the existing ProductivityAgent methods as the base for our tools.
# However, to make them LangChain compatible, we wrap them or redefine them.
# The original file has static methods or instance methods that don't look purely static.
# Let's import the necessary functions directly if possible, or wrap them.

from tools import google_auth
# from api.notes import add_note # Function does not exist
# from api.todos import add_todo # Function does not exist
from datetime import datetime
import uuid

# Import database dependencies
from database import SessionLocal
from database.models import Note

# Import in-memory todos store (for now, as per current architecture)
from api.todos import todos_store, Todo


# It seems `ProductivityAgent` in `productivity_tools.py` had some methods.
# We will create proper LangChain tools here.

@tool
def fetch_recent_emails(user_id: str) -> dict:
    """
    Fetch recent emails from Gmail.
    Useful for summarizing work or checking for missed messages.
    """
    # Note: In a real app, we need to handle token retrieval securely.
    # The existing code passed 'tokens' to the method.
    # Here we might need to assume we can get tokens for the 'user_id' or context.
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
        notes = session.query(Note).filter(Note.user_email == user_email).order_by(Note.created_at.desc()).all()
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
        new_note = Note(
            user_email=user_email,
            title=title,
            content=content,
            source='ai_agent'
        )
        session.add(new_note)
        session.commit()
        session.refresh(new_note)
        return {
            "status": "success", 
            "note_id": str(new_note.id), 
            "message": f"Note '{title}' created."
        }
    except Exception as e:
        session.rollback()
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

        note = session.query(Note).filter(Note.id == n_uuid).first()
        if not note:
            return {"error": "Note not found."}
        
        session.delete(note)
        session.commit()
        return {"status": "success", "message": "Note deleted."}
    except Exception as e:
        session.rollback()
        return {"error": str(e)}
    finally:
        session.close()

# Todos Tools

@tool
def fetch_todos(user_email: str) -> dict:
    """
    Fetch all todos for a specific user.
    """
    # Filter in-memory store
    user_todos = [t for t in todos_store if t.user_email == user_email]
    # Serialize Pydantic models
    return {"todos": [t.dict() for t in user_todos]}

@tool
def create_todo(user_email: str, text: str, due_date: Optional[str] = None) -> dict:
    """
    Create a new todo item.
    """
    try:
        # Parse date if provided
        parsed_date = None
        if due_date:
            try:
                parsed_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "Invalid date format. Use YYYY-MM-DD."}

        new_todo = Todo(
            id=str(uuid.uuid4()),
            user_email=user_email,
            text=text,
            completed=False,
            due_date=parsed_date,
            created_at=datetime.utcnow()
        )
        todos_store.append(new_todo)
        return {"status": "success", "todo_id": new_todo.id, "message": f"Todo '{text}' created."}
    except Exception as e:
        return {"error": str(e)}

@tool
def delete_todo(todo_id: str) -> dict:
    """
    Delete a todo by its ID.
    """
    global todos_store
    
    # Check if exists
    found = False
    for i, t in enumerate(todos_store):
        if t.id == todo_id:
            del todos_store[i]
            found = True
            break
            
    if found:
        return {"status": "success", "message": "Todo deleted."}
    else:
        return {"error": "Todo not found."}




# Google Tasks Tools

@tool
def get_google_tasks(user_id: str) -> dict:
    """
    Get all tasks from Google Tasks.
    Use this to see the user's task list from Google.
    """
    from state.user_tokens import get_user_tokens, user_tokens_store
    
    tokens = get_user_tokens(user_id)
    if not tokens and user_tokens_store:
        # Fallback to any available token for demo
        tokens = next(iter(user_tokens_store.values()))
    
    if not tokens:
        return {"error": "No Google tokens found. User needs to sign in."}
    
    try:
        service = google_auth.get_tasks_service(tokens)
        tasks = google_auth.fetch_tasks(service)
        
        formatted_tasks = [{
            "title": task.get('title', 'Untitled'),
            "status": task.get('status', 'needsAction'),
            "due": task.get('due'),
            "notes": task.get('notes', '')[:100] if task.get('notes') else None
        } for task in tasks]
        
        return {"google_tasks": formatted_tasks, "count": len(formatted_tasks)}
    except Exception as e:
        return {"error": f"Failed to fetch Google Tasks: {str(e)}"}


@tool
def create_google_task(user_id: str, title: str, notes: Optional[str] = None) -> dict:
    """
    Create a new task in Google Tasks.
    Args:
        user_id: The user's ID for token lookup
        title: The title of the task
        notes: Optional description/notes for the task
    """
    from state.user_tokens import get_user_tokens, user_tokens_store
    
    tokens = get_user_tokens(user_id)
    if not tokens and user_tokens_store:
        tokens = next(iter(user_tokens_store.values()))
    
    if not tokens:
        return {"error": "No Google tokens found. User needs to sign in."}
    
    try:
        service = google_auth.get_tasks_service(tokens)
        result = google_auth.create_task(service, title, notes)
        return {"status": "success", "task_id": result.get('id'), "message": f"Task '{title}' created in Google Tasks."}
    except Exception as e:
        return {"error": f"Failed to create Google Task: {str(e)}"}


@tool  
def get_email_summary(user_id: str) -> dict:
    """
    Get a summary of recent emails highlighting urgent items and action items.
    Use this when the user asks about their email priorities or what needs attention.
    """
    import os
    from langchain_groq import ChatGroq
    from state.user_tokens import get_user_tokens, user_tokens_store
    
    tokens = get_user_tokens(user_id)
    if not tokens and user_tokens_store:
        tokens = next(iter(user_tokens_store.values()))
    
    if not tokens:
        return {"error": "No Google tokens found. User needs to sign in."}
    
    try:
        service = google_auth.get_gmail_service(tokens)
        email_ids = google_auth.fetch_recent_emails(service, max_results=5)
        
        emails = []
        for email_meta in email_ids:
            details = google_auth.get_email_details(service, email_meta['id'])
            emails.append(details)
        
        if not emails:
            return {"summary": "No recent emails found.", "email_count": 0}
        
        email_text = "\n\n".join([
            f"From: {e['sender']}\nSubject: {e['subject']}\nDate: {e['date']}\nContent: {e['body'][:500]}"
            for e in emails
        ])
        
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = f"""Summarize these emails in 2-3 sentences. Highlight:
1. Urgent items needing immediate attention
2. Action items to respond to

Emails:
{email_text}

Brief summary:"""

        response = llm.invoke(prompt)
        
        return {"summary": response.content, "email_count": len(emails)}
    except Exception as e:
        return {"error": f"Failed to summarize emails: {str(e)}"}


# All productivity tools list
PRODUCTIVITY_TOOLS = [
    fetch_recent_emails,
    fetch_notes,
    create_note,
    delete_note,
    fetch_todos,
    create_todo,
    delete_todo,
    get_google_tasks,
    create_google_task,
    get_email_summary
]
