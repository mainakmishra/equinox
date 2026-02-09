"""
Morning Briefing API Endpoints
"""

from fastapi import APIRouter
from pydantic import BaseModel
from agents.briefing import generate_briefing

router = APIRouter()


class BriefingRequest(BaseModel):
    email: str


@router.post("/api/briefing/generate")
async def get_morning_briefing(req: BriefingRequest):
    """
    Generate morning briefing for user
    
    Combines:
    - Health/wellness data (sleep score)
    - Critical emails count
    - Tasks for today
    - AI-generated summary
    """
    briefing = await generate_briefing(req.email)
    return briefing
