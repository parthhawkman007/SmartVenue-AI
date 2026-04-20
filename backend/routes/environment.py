from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any
from models.schemas import EnvironmentResponse, APIResponse, success_response, EventType
from firestore.database import is_system_active
from services.auth import get_current_user
import random

router = APIRouter()

@router.get("/environment", response_model=APIResponse[EnvironmentResponse])
async def get_environment(event: EventType = EventType.F1, user: dict = Depends(get_current_user)) -> Any:
    """Simulates or retrieves meteorological conditions."""
    if not await is_system_active():
        raise HTTPException(
            status_code=503,
            detail="System is currently idle. Waiting for administrative activation."
        )
        
    try:
        if event == EventType.FOOTBALL:
            conditions = ["Clear", "Light Rain", "Overcast", "Windy"]
            phase = random.choice(["Pre-Match Build Up", "First Half Operations", "Halftime Intercept", "Full Time Exit Phase"])
        else:
            conditions = ["Sunny skies", "Hot track", "Rain expected in 20m", "Overcast"]
            phase = random.choice(["Grid Formation", "Race Start", "Mid-Race Pit Cycles", "Post-Race Paddock Phase"])
            
        payload = EnvironmentResponse(
            event_phase=phase,
            weather_condition=random.choice(conditions),
            temperature_celsius=random.randint(18, 38),
            humidity_percent=random.randint(20, 85)
        )
        return success_response(payload, "Environment fetched perfectly")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to synthesize environmental data.")
