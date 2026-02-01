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
