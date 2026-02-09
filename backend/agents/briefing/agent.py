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
    
    # 3. Get tasks count
    tasks_today = 0
    schedule_updated = False
    task_titles = []
    
    try:
        # Local Todos
        from database.operations import get_all_todos
        todos = get_all_todos(user_email)
        if todos:
            local_incomplete = [t for t in todos if not t.get("completed", False)]
            tasks_today += len(local_incomplete)
            task_titles.extend([t['text'] for t in local_incomplete])
        
        # Google Tasks
        from state.user_tokens import get_user_tokens
        from tools.google_auth import get_tasks_service, fetch_tasks
        
        tokens = get_user_tokens(user_email)
        if tokens:
            try:
                task_service = get_tasks_service(tokens)
                google_tasks = fetch_tasks(task_service, '@default')
                # Count incomplete google tasks
                g_incomplete = [t for t in google_tasks if t.get('status') != 'completed']
                tasks_today += len(g_incomplete)
                task_titles.extend([t.get('title', 'Untitled') for t in g_incomplete])
                print(f"Debug: Found {len(g_incomplete)} Google tasks for {user_email}")
            except Exception as e:
                print(f"Google Tasks fetch error in briefing: {e}")

        schedule_updated = tasks_today > 0
    except Exception as e:
        print(f"Tasks fetch error: {e}")
    
    # 2. Get emails (Moved after tasks for better context flow)
    critical_emails = 0
    email_summaries = []
    try:
        from tools.google_auth import get_gmail_service, fetch_recent_emails
        
        if tokens: # Re-use tokens from above
            service = get_gmail_service(tokens)
            # Fetch specifically unread emails to get accurate critical count
            emails = fetch_recent_emails(service, max_results=10, query='is:unread')
            
            for e in emails:
                # Get details for better context
                # We need a helper to get snippet if not present, but fetch_recent_emails usually returns snippet
                snippet = e.get('snippet', '')
                
                # Naive critical check: UNREAD from 'important' people or just UNREAD?
                # For now, just count UNREAD
                is_unread = 'UNREAD' in e.get('labelIds', [])
                if is_unread:
                    critical_emails += 1
                
                # Get subject (need to fetch full message for subject usually, but let's try to use snippet)
                # Actually fetch_recent_emails in google_auth.py only does listing.
                # We should get details if we want good summary.
                # But for speed, let's use the list result which has threadId and snippet.
                # To get Subject, we need 'payload' which isn't always in list response unless fields specified.
                # Let's trust the LLM to infer from snippet or just generic "Emails".
                # Improving specific email fetching would start to be slow.
                # Let's add a quick subject fetch if we can, or just use snippet.
                email_summaries.append(f"- {snippet[:100]}...")

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
