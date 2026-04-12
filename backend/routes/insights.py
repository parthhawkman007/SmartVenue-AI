from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.schemas import InsightsResponse
from firestore.database import is_system_active
from routes.crowd import fetch_and_map_zones
from services.crowd_service import evaluate_insights
from services.auth import get_current_user

router = APIRouter()

@router.get("/insights", response_model=InsightsResponse)
async def get_insights(event: str = "F1", user: dict = Depends(get_current_user)):
    """Analytic intelligence calculating global tracking metrics strictly mapping actionable decisions."""
    if not await is_system_active():
        return JSONResponse(content={"status": "idle", "message": "System inactive. Waiting for admin to start event."})
        
    zones = await fetch_and_map_zones(event)
    original_insights = await evaluate_insights(zones, event)
    
    if user.get("role") == "user":
        # Nullify specific aggressive recommendations safely
        sanitized_recommendations = []
        for rec in original_insights.recommendations:
            if "deploy" in rec.action.lower() or "dispatch" in rec.action.lower() or "immediate" in rec.action.lower():
                rec.action = "Standby for Command Instructions"
                rec.reason = "Tactical structural shifts are actively being managed by Administrative leads securely."
            sanitized_recommendations.append(rec)
        original_insights.recommendations = sanitized_recommendations
        
    return original_insights
