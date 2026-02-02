# supervisor state

from typing import TypedDict, Annotated, Sequence, Optional, Literal
from langchain_core.messages import BaseMessage
import operator

class SupervisorState(TypedDict):
    """state for the supervisor graph"""
    
    # conversation
    messages: Annotated[Sequence[BaseMessage], operator.add]
    
    # routing
    next: Optional[str]
    
    # user context
    user_id: str
    
    # optional final response aggregation
    final_response: Optional[str]
