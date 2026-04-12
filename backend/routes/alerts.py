from fastapi import APIRouter, Depends
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
    """Alert Watchdog specifically filtering immediate dangerous threat bounds seamlessly."""
    if not await is_system_active():
        return JSONResponse(content={"status": "idle", "message": "System inactive. Waiting for admin to start event."})
        
    zones = await fetch_and_map_zones(event)
    alerts = await evaluate_alerts(zones, event)
    
    if user.get("role") == "user":
        # Strict backend enforcement safely stripping out critical threats natively
        alerts = [a for a in alerts if a.level != "critical"]
        
    return alerts
