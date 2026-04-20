from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from models.schemas import InsightsResponse, APIResponse, success_response, EventType
from firestore.database import is_system_active
from routes.crowd import fetch_and_map_zones
from services.crowd_service import evaluate_insights
from services.auth import get_current_user

router = APIRouter()

@router.get("/insights", response_model=APIResponse[InsightsResponse])
async def get_insights(event: EventType = EventType.F1, user: dict = Depends(get_current_user)) -> Any:
    """Generates AI-driven tactical insights and recommendations based on current zone density."""
    if not await is_system_active():
        raise HTTPException(
            status_code=503,
            detail="System is currently idle. Waiting for administrative activation."
        )
        
    zones = await fetch_and_map_zones(event)
    original_insights = await evaluate_insights(zones, event)
    
    if user.get("role") == "user":
        # Mask administrative/tactical recommendations for standard user roles
        sanitized_recommendations = []
        for rec in original_insights.recommendations:
            if any(term in rec.action.lower() for term in ["deploy", "dispatch", "immediate"]):
                rec.action = "Standby for Command Instructions"
                rec.reason = "Tactical structural shifts are actively being managed by Administrative leads securely."
            sanitized_recommendations.append(rec)
        original_insights.recommendations = sanitized_recommendations
        
    return success_response(original_insights, "Intelligence successfully processed")
