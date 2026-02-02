# productivity agent state

from typing import TypedDict, Annotated, Sequence, Optional
from langchain_core.messages import BaseMessage
import operator

class ProductivityState(TypedDict):
    """state for the productivity agent graph"""
    
    # conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # user context
    user_id: str
    
    # task data (optional/example fields)
    recent_emails: Optional[list]
    notes: Optional[list]
    todos: Optional[list]
    
    # output control
    response: Optional[str]
