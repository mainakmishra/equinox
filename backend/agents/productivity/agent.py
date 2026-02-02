# productivity agent - langgraph implementation

import os
from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

from .state import ProductivityState
from .tools import PRODUCTIVITY_TOOLS

SYSTEM_PROMPT = """You are a helpful productivity assistant named Equinox Work.

Your job is to help users manage their tasks, emails, and notes.
You have access to tools that can:
- Fetch recent emails
- Create notes
- Create todo items

Guidelines:
1. Be efficient and professional.
2. If a user asks to summarize emails, fetch them first.
3. If a user wants to remember something, suggest creating a note or todo.
4. Always check for necessary information (like title for a note) before calling a tool.
"""

def create_productivity_agent():
    """create and return the productivity agent graph"""
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.5,
        api_key=os.getenv("GROQ_API_KEY")
    )
    llm_with_tools = llm.bind_tools(PRODUCTIVITY_TOOLS)
    
    def call_model(state: ProductivityState):
        messages = state["messages"]
        user_id = state.get("user_id", "unknown_user")
        
        # Check if system message exists
        if not any(isinstance(m, SystemMessage) for m in messages):
            # Inject user context
            context_prompt = f"{SYSTEM_PROMPT}\n\nCurrent User Email: {user_id}\nUse this email for all tool calls that require 'user_email'."
            messages = [SystemMessage(content=context_prompt)] + list(messages)
            
        response = llm_with_tools.invoke(messages)
        return {"messages": [response]}
    
    def should_continue(state: ProductivityState) -> Literal["tools", "end"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "end"
        
    graph = StateGraph(ProductivityState)
    
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(PRODUCTIVITY_TOOLS))
    
    graph.set_entry_point("agent")
    
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {"tools": "tools", "end": END}
    )
    graph.add_edge("tools", "agent")
    
    return graph.compile()


_productivity_agent = None

def get_productivity_agent():
    global _productivity_agent
    if _productivity_agent is None:
        _productivity_agent = create_productivity_agent()
    return _productivity_agent
