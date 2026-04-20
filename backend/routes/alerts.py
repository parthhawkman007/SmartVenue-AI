from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Any
from ..models.schemas import Alert, APIResponse, success_response, EventType
from ..firestore.database import is_system_active
from .crowd import fetch_and_map_zones
from ..services.crowd_service import evaluate_alerts
from ..services.auth import get_current_user

router = APIRouter()

@router.get("/alerts", response_model=APIResponse[List[Alert]])
async def get_alerts(event: EventType = EventType.F1, user: dict = Depends(get_current_user)) -> Any:
    """Retrieves actively tracked security and safety alerts for the designated domain."""
    if not await is_system_active():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="System is currently idle. Waiting for administrative activation."
        )
        
    try:
        zones = await fetch_and_map_zones(event)
        alerts = await evaluate_alerts(zones, event)
        
        if user.get("role") == "user":
            # Filter out critical alerts for standard user roles
            alerts = [a for a in alerts if a.level != "critical"]
            
        return success_response(alerts, "Alerts verified safely")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to retrieve intelligence alerts.")
