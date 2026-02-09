"""
Morning Briefing Agent
Orchestrates wellness and productivity data to generate daily briefing
"""

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import os


async def generate_briefing(user_email: str) -> dict:
    """
    Generate morning briefing combining health + productivity data
    
    Args:
        user_email: User's email address
        
    Returns:
        dict with greeting, sleep_score, critical_emails, schedule_updated, summary
    """
    user_email = user_email.lower()
    
    # 1. Get health data
    sleep_score = 0
    try:
        from database.operations import get_latest_health_log
        health_log = get_latest_health_log(user_email)
        
        if health_log:
            # Calculate sleep score (0-100 based on hours)
            sleep_hours = health_log.get("sleep_hours", 0)
            sleep_score = min(int(sleep_hours * 12), 100)  # 8h = 96 points
    except Exception as e:
        print(f"Health data fetch error: {e}")
    
    # 2. Get Tasks & Emails
    tasks_today = 0
    schedule_updated = False
    task_titles = []
    critical_emails = 0
    email_summaries = []
    
    # Get tokens ONCE for both services
    try:
        from state.user_tokens import get_user_tokens
        tokens = get_user_tokens(user_email)
    except Exception as e:
        print(f"Token fetch error: {e}")
        tokens = None

    # TASKS
    try:
        # Use the unified service that gets Local + Google tasks
        from api.todos import get_todos_service
        
        # This returns List[TodoResponse]
        all_todos = get_todos_service(db, user_email)
        
        # Filter for incomplete
        incomplete_todos = [t for t in all_todos if not t.completed]
        tasks_today = len(incomplete_todos)
        schedule_updated = tasks_today > 0
        task_titles = [t.text for t in incomplete_todos]
        
    except Exception as e:
        print(f"Tasks fetch error: {e}")

    # EMAILS
    if tokens:
        try:
            from tools.google_auth import get_gmail_service, fetch_recent_emails
            
            service = get_gmail_service(tokens)
            # Fetch specifically unread emails
            emails = fetch_recent_emails(service, max_results=10, query='is:unread')
            critical_emails = len(emails)
            
            # Get snippets for first 5 for the summary
            for e in emails[:5]:
                snippet = e.get('snippet', '')
                email_summaries.append(f"- {snippet[:150]}...")
                
        except Exception as e:
            print(f"Email fetch error: {e}")

    # 4. Generate AI summary
    summary = ""
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )
        
        prompt = ChatPromptTemplate.from_template(
            """You are a helpful AI assistant creating a brief morning summary.
            
            User's data:
            - Sleep score: {sleep_score}/100 (If 0, assume no data tracked)
            - Unread Emails: {emails}
            - Recent Email Snippets: {email_context}
            - Tasks Count: {tasks}
            - Task List: {task_list}
            
            Generate a warm, encouraging morning briefing (max 3 sentences).
            1. Acknowledge their health status (if sleep score > 0). If 0, suggest tracking sleep or taking it easy.
            2. Mention their workload (tasks). Mention specific high-priority sounding tasks if any.
            3. Mention if checking emails is urgent based on snippets.
            
            Keep it friendly, concise, and actionable.
            """
        )
        
        chain = prompt | llm
        response = chain.invoke({
            "sleep_score": sleep_score,
            "emails": critical_emails,
            "email_context": "; ".join(email_summaries) if email_summaries else "No recent emails",
            "tasks": tasks_today,
            "task_list": ", ".join(task_titles[:5]) # Pass first 5 task titles
        })
        
        summary = response.content
    except Exception as e:
        print(f"LLM summary error: {e}")
        summary = "Have a great day! Focus on your priorities."
    
    # Extract user name from email
    user_name = user_email.split('@')[0].title()
    
    return {
        "greeting": f"Good morning, {user_name}",
        "sleep_score": sleep_score,
        "critical_emails": critical_emails,
        "schedule_updated": schedule_updated,
        "tasks_count": tasks_today,
        "summary": summary
    }
