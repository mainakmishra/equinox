# backend/agents/productivity/productivity_tools.py

import os
from datetime import datetime
from tools import google_auth

# LLM for summarization
from langchain_groq import ChatGroq


class ProductivityAgent:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            api_key=os.getenv("GROQ_API_KEY")
        )

    def handle_supervisor_instruction(self, action, params):
        """Handle instructions from supervisor agent"""
        if action == 'reschedule':
            print(f"Rescheduling {params['from']} to {params['to']}")
            if params.get('suggest_nap'):
                print("Suggesting a 20-minute power nap slot.")

    # ---------- Email Functions ----------

    def get_today_priorities(self, tokens):
        """Fetch recent emails and return basic info"""
        service = google_auth.get_gmail_service(tokens)
        emails = google_auth.fetch_recent_emails(service, max_results=5)
        return {"recent_emails": emails}

    def get_email_summaries(self, tokens, max_emails: int = 5):
        """Fetch recent emails with full content"""
        service = google_auth.get_gmail_service(tokens)
        email_ids = google_auth.fetch_recent_emails(service, max_results=max_emails)
        
        emails = []
        for email_meta in email_ids:
            details = google_auth.get_email_details(service, email_meta['id'])
            emails.append(details)
        
        return emails

    def summarize_emails(self, tokens, max_emails: int = 5):
        """Fetch emails and summarize with LLM"""
        emails = self.get_email_summaries(tokens, max_emails)
        
        if not emails:
            return {"summary": "No emails found.", "emails": []}
        
        # Format emails for LLM
        email_text = "\n\n".join([
            f"From: {e['sender']}\nSubject: {e['subject']}\nDate: {e['date']}\nContent: {e['body'][:500]}"
            for e in emails
        ])
        
        prompt = f"""Summarize these emails concisely. Highlight:
1. Urgent items that need immediate attention
2. Action items I need to respond to
3. Key information I should know

Emails:
{email_text}

Provide a brief, actionable summary:"""

        response = self.llm.invoke(prompt)
        
        return {
            "summary": response.content,
            "email_count": len(emails),
            "emails": [{"subject": e['subject'], "sender": e['sender']} for e in emails]
        }

    # ---------- Google Tasks Functions ----------

    def get_tasks(self, tokens):
        """Get all tasks from Google Tasks"""
        service = google_auth.get_tasks_service(tokens)
        return google_auth.fetch_tasks(service)

    def get_task_lists(self, tokens):
        """Get all task lists"""
        service = google_auth.get_tasks_service(tokens)
        return google_auth.fetch_task_lists(service)

    def add_google_task(self, tokens, title: str, notes: str = None, due: str = None):
        """Create a new task in Google Tasks"""
        service = google_auth.get_tasks_service(tokens)
        return google_auth.create_task(service, title, notes, due)

    def complete_google_task(self, tokens, task_id: str):
        """Mark a task as completed"""
        service = google_auth.get_tasks_service(tokens)
        return google_auth.complete_task(service, task_id)

    # ---------- Notes/Todo Functions (use database directly) ----------

    def agent_add_note(self, db_session, user_email: str, title: str, content: str, source: str = "agent"):
        """Add a note via database (for agent use)"""
        from database.models import Note
        
        note = Note(
            user_email=user_email,
            title=title,
            content=content,
            source=source
        )
        db_session.add(note)
        db_session.commit()
        db_session.refresh(note)
        return note

    def agent_add_todo(self, db_session, user_email: str, text: str, due_date=None):
        """Add a todo via database (for agent use)"""
        from database.models import Todo
        
        todo = Todo(
            user_email=user_email,
            text=text,
            completed=False,
            due_date=due_date
        )
        db_session.add(todo)
        db_session.commit()
        db_session.refresh(todo)
        return todo