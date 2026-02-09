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
    
    # 2. Get email count
    critical_emails = 0
    try:
        from state.user_tokens import get_user_tokens
        from tools.google_auth import get_gmail_service, fetch_recent_emails
        
        tokens = get_user_tokens(user_email)
        if tokens:
            service = get_gmail_service(tokens)
            emails = fetch_recent_emails(service, max_results=10)
            # Count unread important emails
            critical_emails = len([e for e in emails if 'UNREAD' in e.get('labelIds', [])])
    except Exception as e:
        print(f"Email fetch error: {e}")
    
    # 3. Get tasks count
    tasks_today = 0
    schedule_updated = False
    try:
        from database.operations import get_all_todos
        todos = get_all_todos(user_email)
        if todos:
            # Count incomplete tasks
            tasks_today = len([t for t in todos if not t.get("completed", False)])
            schedule_updated = tasks_today > 0
    except Exception as e:
        print(f"Tasks fetch error: {e}")
    
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
            - Sleep score: {sleep_score}/100
            - Critical emails: {emails}
            - Tasks today: {tasks}
            
            Generate a warm, encouraging 2-3 sentence morning briefing.
            Focus on what they should prioritize today based on their readiness.
            If sleep is low (<70), suggest lighter tasks.
            Keep it friendly and actionable.
            """
        )
        
        chain = prompt | llm
        response = chain.invoke({
            "sleep_score": sleep_score,
            "emails": critical_emails,
            "tasks": tasks_today
        })
        
        summary = response.content
    except Exception as e:
        print(f"LLM summary error: {e}")
        summary = "Have a great day! Focus on your priorities and take breaks when needed."
    
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
