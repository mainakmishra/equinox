import os
import requests
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from sqlalchemy.orm import Session

from database import get_db, User
from state.user_tokens import save_user_tokens

router = APIRouter()

CLIENT_SECRET_PATH = os.path.join(
    os.path.dirname(__file__), "client_secret.json"
)

REDIRECT_URI = "http://localhost:8000/auth/google/callback"

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/tasks",  # Google Tasks API
]


@router.get("/auth/google/login")
def google_login():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    auth_url, _ = flow.authorization_url(
        access_type="offline",
        prompt="consent",
        include_granted_scopes="true",
    )

    return {"auth_url": auth_url}


@router.get("/auth/google/callback")
def google_callback(request: Request, db: Session = Depends(get_db)):
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRET_PATH,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI,
    )

    flow.fetch_token(authorization_response=str(request.url))
    credentials = flow.credentials

    # Fetch user profile
    userinfo_response = requests.get(
        "https://www.googleapis.com/oauth2/v2/userinfo",
        headers={"Authorization": f"Bearer {credentials.token}"},
        timeout=10,
    )
    userinfo_response.raise_for_status()
    userinfo = userinfo_response.json()

    google_email = userinfo["email"]
    name = userinfo.get("name")
    avatar_url = userinfo.get("picture")

    # Find or create user
    user = db.query(User).filter(User.email == google_email).first()
    if not user:
        user = User(
            email=google_email,
            name=name,
            avatar_url=avatar_url,
        )
        db.add(user)
    else:
        user.name = name
        user.avatar_url = avatar_url

    db.commit()
    db.refresh(user)

    # Store tokens securely
    tokens = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

    save_user_tokens(str(user.id), tokens)

    return RedirectResponse(
        f"http://localhost:5173/chat?email={google_email}"
    )


# ---------- Gmail utilities ----------

def get_gmail_service(tokens: dict):
    creds = Credentials(**tokens)
    return build("gmail", "v1", credentials=creds)


def fetch_recent_emails(service, max_results: int = 5):
    results = service.users().messages().list(
        userId="me",
        maxResults=max_results,
    ).execute()

    return results.get("messages", [])


def get_email_details(service, message_id: str) -> dict:
    """Fetch full email content including subject, sender, and body"""
    import base64
    
    msg = service.users().messages().get(
        userId='me',
        id=message_id,
        format='full'
    ).execute()
    
    headers = msg.get('payload', {}).get('headers', [])
    
    # Extract subject and sender from headers
    subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
    sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
    date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
    
    # Extract body - handle different payload structures
    body = ''
    payload = msg.get('payload', {})
    
    if 'body' in payload and payload['body'].get('data'):
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    elif 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain' and part.get('body', {}).get('data'):
                body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                break
    
    return {
        'id': message_id,
        'subject': subject,
        'sender': sender,
        'date': date,
        'snippet': msg.get('snippet', ''),
        'body': body[:1000] if body else msg.get('snippet', '')  # Limit body size
    }


# ---------- Google Tasks utilities ----------

def get_tasks_service(tokens: dict):
    """Get Google Tasks API service"""
    creds = Credentials(**tokens)
    return build("tasks", "v1", credentials=creds)


def fetch_task_lists(service):
    """Get all task lists"""
    results = service.tasklists().list().execute()
    return results.get('items', [])


def fetch_tasks(service, tasklist_id: str = '@default'):
    """Get all tasks from a task list"""
    results = service.tasks().list(tasklist=tasklist_id).execute()
    return results.get('items', [])


def create_task(service, title: str, notes: str = None, due: str = None, tasklist_id: str = '@default'):
    """Create a new task in Google Tasks
    
    Args:
        service: Google Tasks service
        title: Task title
        notes: Optional task notes/description
        due: Optional due date in RFC 3339 format (e.g., '2026-02-03T00:00:00.000Z')
        tasklist_id: Task list ID, defaults to '@default'
    """
    task = {'title': title}
    if notes:
        task['notes'] = notes
    if due:
        task['due'] = due
    
    return service.tasks().insert(tasklist=tasklist_id, body=task).execute()


def complete_task(service, task_id: str, tasklist_id: str = '@default'):
    """Mark a task as completed"""
    task = service.tasks().get(tasklist=tasklist_id, task=task_id).execute()
    task['status'] = 'completed'
    return service.tasks().update(tasklist=tasklist_id, task=task_id, body=task).execute()

