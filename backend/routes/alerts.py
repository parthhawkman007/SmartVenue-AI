from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List
from models.schemas import Alert
from firestore.database import is_system_active
from routes.crowd import fetch_and_map_zones
from services.crowd_service import evaluate_alerts
from services.auth import get_current_user

router = APIRouter()

@router.get("/alerts", response_model=List[Alert])
async def get_alerts(event: str = "F1", user: dict = Depends(get_current_user)):
    """
    Retrieves a list of active security and safety alerts for the specified event domain.
    
    - **event**: The physical domain mapping (e.g., 'F1', 'Football').
    - **user**: Automated session context from Firebase Auth.
    
    Roles:
    - **Admin**: Receives all alerts including critical infrastructure threats.
    - **User**: Receives filtered non-critical safety alerts only.
    """
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
            
        return alerts
    except Exception as e:
        print(f"[ALERTS ERROR] {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve intelligence alerts.")
