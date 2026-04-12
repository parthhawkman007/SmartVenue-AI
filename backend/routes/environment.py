from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from models.schemas import EnvironmentResponse
from firestore.database import is_system_active
from services.auth import get_current_user
import random

router = APIRouter()

@router.get("/environment", response_model=EnvironmentResponse)
async def get_environment(event: str = "F1", user: dict = Depends(get_current_user)):
    """Mock meteorological and physical pipeline statuses natively bounding states."""
    if not await is_system_active():
        return JSONResponse(content={"status": "idle", "message": "System inactive. Waiting for admin to start event."})
        
    # Build robust variations mirroring structural states effortlessly
    if event.lower() == "football":
        conditions = ["Clear", "Light Rain", "Overcast", "Windy"]
        phase = random.choice(["Pre-Match Build Up", "First Half Operations", "Halftime Intercept", "Full Time Exit Phase"])
    else:
        conditions = ["Sunny skies", "Hot track", "Rain expected in 20m", "Overcast"]
        phase = random.choice(["Grid Formation", "Race Start", "Mid-Race Pit Cycles", "Post-Race Paddock Phase"])
        
    return EnvironmentResponse(
        event_phase=phase,
        weather_condition=random.choice(conditions),
        temperature_celsius=random.randint(18, 38),
        humidity_percent=random.randint(20, 85)
    )
