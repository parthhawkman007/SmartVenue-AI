from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Any
import logging

from models.schemas import ZoneDensity, APIResponse, success_response, EventType
from firestore.database import db, is_system_active
from services.crowd_service import compute_trend, map_zone_names
from services.simulator_service import generate_simulated_data
from services.auth import get_current_user, require_admin

router = APIRouter()
logger = logging.getLogger(__name__)

FALLBACK_CACHE: List[ZoneDensity] = []

async def fetch_current_zones() -> List[ZoneDensity]:
    """Retrieve realtime zones from firestore safely."""
    if db is None:
        raise ValueError("Firestore uninitialized")
    
    crowd_ref = db.collection("crowd_data")
    docs = [d async for d in crowd_ref.stream()]
    if not docs:
        raise ValueError("Empty firestore collection")
        
    zones = []
    for doc in docs:
        data = doc.to_dict()
        data["source"] = "firestore"
        try:
            zones.append(ZoneDensity(**data))
        except Exception:
            pass 
            
    if not zones: raise ValueError("No valid parseable geometries found")
    return zones

def fallback_zones() -> List[ZoneDensity]:
    """Graceful static memory fallback."""
    global FALLBACK_CACHE
    if FALLBACK_CACHE: return FALLBACK_CACHE.copy()
    
    return [
        ZoneDensity(zone="Main Entrance", density=85, status="Very Crowded", source="fallback"),
        ZoneDensity(zone="Food Court", density=60, status="Moderate", source="fallback"),
        ZoneDensity(zone="Restrooms", density=15, status="Low", source="fallback"),
        ZoneDensity(zone="VIP Lounge", density=5, status="Low", source="fallback"),
        ZoneDensity(zone="Stage Area A", density=98, status="Very Crowded", source="fallback")
    ]

async def fetch_and_map_zones(event: EventType) -> List[ZoneDensity]:
    try:
        zones = await fetch_current_zones()
    except Exception as exc:
        logger.warning("Falling back to cached zones because Firestore fetch failed: %s", type(exc).__name__)
        zones = fallback_zones()

    # Deep memory mapping for drift computations and domain logic translating
    for z in zones:
        raw_zone = z.zone
        z.trend = compute_trend(raw_zone, z.density)
        z.zone = map_zone_names(raw_zone, event)
        z.event_type = event
        
    return zones

@router.get("/crowd", response_model=APIResponse[List[ZoneDensity]])
async def get_crowd(event: EventType = EventType.F1, user: dict = Depends(get_current_user)) -> Any:
    """Retrieves real-time crowd density metrics across all monitored zones."""
    if not await is_system_active():
        raise HTTPException(
            status_code=503,
            detail="System is currently idle. Waiting for administrative activation."
        )
    
    try:
        zones = await fetch_and_map_zones(event)
        return success_response(zones, "Crowd streams retrieved successfully")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to retrieve crowd density streams.")

@router.post("/crowd", response_model=APIResponse[ZoneDensity], status_code=status.HTTP_201_CREATED)
async def create_or_update_crowd_density(
    data: ZoneDensity,
    _: dict = Depends(require_admin),
) -> Any:
    """Ingests physical IoT metrics."""
    if db is None:
        raise HTTPException(status_code=503, detail="Database instance unavailable.")

    try:
        doc_ref = db.collection("crowd_data").document(data.zone)
        await doc_ref.set(data.model_dump())
        return success_response(data, "Density metrics committed safely")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to persist crowd density metrics.")

@router.get("/simulate", response_model=APIResponse[List[ZoneDensity]])
async def simulate_crowd(event: EventType = EventType.F1, user: dict = Depends(require_admin)) -> Any:
    """Rapid testing endpoint heavily jittering trends."""
    if not await is_system_active():
        return {"status": "idle", "data": None, "message": "System inactive. Waiting for admin to start event."}
        
    global FALLBACK_CACHE
    zones = generate_simulated_data(event)
    
    FALLBACK_CACHE = [ZoneDensity(**z.model_dump()) for z in zones]
    
    for z in zones:
        raw_zone = z.zone
        z.trend = compute_trend(raw_zone, z.density)
        
        if db is not None:
            try:
                await db.collection("crowd_data").document(raw_zone).set(z.model_dump())
            except Exception as exc:
                logger.warning("Failed to persist simulated zone '%s': %s", raw_zone, exc)
                 
        z.zone = map_zone_names(raw_zone, event)
        
    return success_response(zones, "Simulation metrics updated")
