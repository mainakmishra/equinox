# equinox backend

import os
from dotenv import load_dotenv

# load env vars from backend directory
# load env vars from backend directory
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(env_path)
print(f"Loading env from {env_path}")
print(f"OPIK_API_KEY present: {'OPIK_API_KEY' in os.environ}")

# required for local oauth testing
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from opik.integrations.langchain import OpikTracer

# supervisor and productivity agents
# from supervisor.supervisor_agent import SupervisorAgent # Removed

from state.user_tokens import get_user_tokens
from tools.google_auth import router as google_auth_router, get_gmail_service, fetch_recent_emails

from api.notes import router as notes_router
from api.todos import router as todos_router
# wellness agent api routes
from api import api_router
from api.profile import router as profile_router

from api.notes import router as notes_router
from api.todos import router as todos_router



groq_api_key = os.getenv("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY not set - check .env file")

client = Groq(api_key=groq_api_key)

app = FastAPI(
    title="Equinox API",
    description="multi-agent wellness and productivity backend",
    version="0.1.0"
)

# cors setup - allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://equinox-six-xi.vercel.app",
        "https://equinox.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# wellness api routes
app.include_router(api_router)

# profile api routes (top-level, not under /api)
app.include_router(profile_router)

# google auth routes
app.include_router(google_auth_router)


app.include_router(notes_router)
app.include_router(todos_router)

from api.history import router as history_router
app.include_router(history_router)

from api.emails import router as emails_router
app.include_router(emails_router)

class ChatRequest(BaseModel):
    message: str
    email: str | None = None
    thread_id: str | None = None


@app.get("/ping")
def ping():
    return {"message": "hello from equinox", "status": "ok"}


@app.post("/supervisor")
def supervisor_endpoint(req: ChatRequest):
    """trigger supervisor agent to get work summary or handle request"""
    # Note: Using ChatRequest which has 'message' field
    user_id = req.email if req.email else "demo_user"
    
    from supervisor.supervisor_agent import get_supervisor_graph
    from langchain_core.messages import HumanMessage
    
    import uuid
    thread_id = req.thread_id if req.thread_id else str(uuid.uuid4())
    
    supervisor = get_supervisor_graph()
    
    initial_state = {
        "messages": [HumanMessage(content=req.message)],
        "user_id": user_id,
        "next": None
    }
    
    try:
        # Pass thread_id in metadata for Opik
        result = supervisor.invoke(initial_state, config={
            "callbacks": [OpikTracer(project_name="equinox")],
            "metadata": {"thread_id": thread_id}
        })
        last_message = result["messages"][-1]
        return {"reply": last_message.content, "thread_id": thread_id}
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"reply": f"Error interacting with supervisor: {str(e)}"}


@app.post("/chat")
async def chat(req: ChatRequest):
    """general chat endpoint with email integration"""
    try:
        user_id = "demo_user"
        tokens = get_user_tokens(user_id)
        
        if tokens:
            service = get_gmail_service(tokens)
            emails = fetch_recent_emails(service)
            if emails:
                email_id = emails[0]["id"]
                email = service.users().messages().get(
                    userId="me", id=email_id, format="metadata"
                ).execute()
                
                subject = None
                for header in email.get("payload", {}).get("headers", []):
                    if header["name"].lower() == "subject":
                        subject = header["value"]
                        break
                
                snippet = email.get("snippet", "")
                reply = f"Most recent email: {subject or 'No Subject'} | {snippet}"
            else:
                reply = "No recent emails found."
        else:
            reply = "No email tokens found. Please sign in with Google."
        
        return {"reply": reply}
    except Exception as e:
        return {"reply": f"Error: {str(e)}"}
    

