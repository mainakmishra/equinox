# backend/agents/productivity_tools.py


from tools import google_auth
from api.notes import add_note
from api.todos import add_todo
from datetime import datetime

class ProductivityAgent:
    def __init__(self):
        # You can add agent state here if needed
        pass

    def handle_supervisor_instruction(self, action, params):
        # Example: handle rescheduling or suggesting a nap
        if action == 'reschedule':
            # Implement logic to reschedule tasks
            print(f"Rescheduling {params['from']} to {params['to']}")
            if params.get('suggest_nap'):
                print("Suggesting a 20-minute power nap slot.")
        # Add more actions as needed

    def get_today_priorities(self, tokens):
        """Fetch recent emails using Gmail tool and summarize."""
        service = google_auth.get_gmail_service(tokens)
        emails = google_auth.fetch_recent_emails(service)
        # For demo, just return the email IDs
        return {"recent_emails": emails}
    
    def agent_add_note(user_email, title, content, user):
        note = {
         "user_email": user_email,
         "title": title,
         "content": content,
         "created_at": datetime.utcnow(),
         "user": user,
         }
        return add_note(note)

    def agent_add_todo(user_email, text, due_date=None):
        todo = {
        "user_email": user_email,
        "text": text,
        "completed": False,
        "due_date": due_date,
        "created_at": datetime.utcnow()
         }
        return add_todo(todo)