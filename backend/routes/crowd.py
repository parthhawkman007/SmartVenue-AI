from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from typing import List
from models.schemas import ZoneDensity
from firestore.database import db, is_system_active
from services.crowd_service import compute_trend, generate_simulated_data, map_zone_names
from services.auth import get_current_user, require_admin

router = APIRouter()

FALLBACK_CACHE: List[ZoneDensity] = []

async def fetch_current_zones() -> List[ZoneDensity]:
    """Helper method serving robust Firestore data safely throwing validation errors on logic fail loops."""
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
    """Graceful static data fallback identical to origin behavior but seamlessly adopting memory drifts natively."""
    global FALLBACK_CACHE
    if FALLBACK_CACHE: return FALLBACK_CACHE.copy()
    
    return [
        ZoneDensity(zone="Main Entrance", density=85, status="Very Crowded", source="fallback"),
        ZoneDensity(zone="Food Court", density=60, status="Moderate", source="fallback"),
        ZoneDensity(zone="Restrooms", density=15, status="Low", source="fallback"),
        ZoneDensity(zone="VIP Lounge", density=5, status="Low", source="fallback"),
        ZoneDensity(zone="Stage Area A", density=98, status="Very Crowded", source="fallback")
    ]

async def fetch_and_map_zones(event: str) -> List[ZoneDensity]:
    try:
        zones = await fetch_current_zones()
    except Exception as e:
        print(f"Using fallback -> Traced DB Issue: {type(e).__name__}")
        zones = fallback_zones()

    # Deep memory mapping for drift computations and domain logic translating
    for z in zones:
        raw_zone = z.zone
        z.trend = compute_trend(raw_zone, z.density)
        z.zone = map_zone_names(raw_zone, event)
        z.event_type = event
        
    return zones

@router.get("/crowd", response_model=List[ZoneDensity])
async def get_crowd(event: str = "F1", user: dict = Depends(get_current_user)):
    """
    Retrieves real-time crowd density metrics across all monitored zones.
    
    - **event**: The physical domain mapping (e.g., 'F1', 'Football').
    
    Returns a list of zones with their calculated density percentage, 
    current status, and observed trends.
    """
    if not await is_system_active():
        raise HTTPException(
            status_code=503,
            detail="System is currently idle. Waiting for administrative activation."
        )
    
    try:
        return await fetch_and_map_zones(event)
    except Exception as e:
        print(f"[CROWD ERROR] {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve crowd density streams.")

@router.post("/crowd", response_model=ZoneDensity, status_code=status.HTTP_201_CREATED)
async def create_or_update_crowd_density(data: ZoneDensity):
    try:
        doc_ref = db.collection("crowd_data").document(data.zone)
        await doc_ref.set(data.model_dump())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed securely.")

@router.get("/simulate", response_model=List[ZoneDensity])
async def simulate_crowd(event: str = "F1", user: dict = Depends(require_admin)):
    """Rapid testing endpoint heavily jittering trends tracking physical deployments seamlessly to state memory maps."""
    if not await is_system_active():
        return JSONResponse(content={"status": "idle", "message": "System inactive. Waiting for admin to start event."})
        
    global FALLBACK_CACHE
    zones = generate_simulated_data(event)
    
    # Cache completely isolated array mapped correctly
    FALLBACK_CACHE = [ZoneDensity(**z.model_dump()) for z in zones]
    
    for z in zones:
        raw_zone = z.zone
        z.trend = compute_trend(raw_zone, z.density)
        
        # Directly execute Firestore commits persistently fixing decoupled insights loops cleanly!
        if db is not None:
             try:
                 await db.collection("crowd_data").document(raw_zone).set(z.model_dump())
             except Exception:
                 pass
                 
        z.zone = map_zone_names(raw_zone, event)
        
    return zones
