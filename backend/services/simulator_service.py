import random
from typing import List
from models.schemas import ZoneDensity, EventType
from services.crowd_service import PREVIOUS_DENSITY

def generate_simulated_data(event: EventType = EventType.F1) -> List[ZoneDensity]:
    """Generates jittered simulated payloads reflecting physical environments."""
    base_zones = ["Main Entrance", "Food Court", "Restrooms", "VIP Lounge", "Stage Area A"]
    event_str = str(event.value).lower()
    
    zones = []
    for base_z in base_zones:
        if event_str == "f1" and base_z in ["Main Entrance", "Stage Area A"]: 
            base_density = random.randint(85, 98)
        elif event_str == "football" and base_z in ["Food Court", "Restrooms"]: 
            base_density = random.randint(80, 95)
        else:
            base_density = PREVIOUS_DENSITY.get(base_z, random.randint(15, 60))
            
        new_density = max(0, min(100, base_density + random.randint(-15, 15)))
        
        status = "Low"
        if new_density > 90: status = "Very Crowded"
        elif new_density > 70: status = "Crowded"
        elif new_density > 30: status = "Moderate"
        
        zones.append(ZoneDensity(
            zone=base_z,
            density=new_density,
            status=status,
            source="simulation",
            event_type=event
        ))
    return zones
