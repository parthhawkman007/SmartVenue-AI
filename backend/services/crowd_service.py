import random
from typing import List, Dict
from ..models.schemas import ZoneDensity, InsightsResponse, Alert, Recommendation, EventType

PREVIOUS_DENSITY: Dict[str, int] = {}

def map_zone_names(zone: str, event_type: EventType) -> str:
    """Translates discrete DB zones into localized physical stadiums."""
    if event_type == EventType.FOOTBALL:
        mapping = {
            "Main Entrance": "Tunnel Entry",
            "Stage Area A": "North Stand",
            "Food Court": "Concourse Food Area",
            "Restrooms": "East Stand",
            "VIP Lounge": "VIP Box"
        }
        return mapping.get(zone, zone)
    
    mapping = {
        "Main Entrance": "Gate A – Grandstand Entry",
        "Stage Area A": "Pit Lane Walk Zone",
        "Food Court": "Fan Zone Food Court",
        "Restrooms": "Circuit Restrooms",
        "VIP Lounge": "Paddock Club Lounge"
    }
    return mapping.get(zone, zone)

def compute_trend(zone: str, current_density: int) -> str:
    """Computes whether crowd density is rising or falling vs previous tracked state."""
    previous = PREVIOUS_DENSITY.get(zone, current_density)
    
    # Store explicit new boundary map overwrites
    PREVIOUS_DENSITY[zone] = current_density
    
    # Analyze trajectory logic
    if current_density > previous + 2:
        return "increasing"
    elif current_density < previous - 2:
        return "decreasing"
    return "stable"

import asyncio
from .gemini_service import generate_insight_async

async def evaluate_insights(zones: List[ZoneDensity], event_type: EventType = EventType.F1) -> InsightsResponse:
    """Evaluates AI insights synchronously tracking memory states."""
    alerts = []
    recommendations = []
    
    tasks = [generate_insight_async(z.zone, z.density, z.trend, str(event_type.value)) for z in zones]
    gemini_responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for z, ai_res in zip(zones, gemini_responses):
        handled = False
        
        if isinstance(ai_res, dict):
            handled = True
            level = ai_res.get("alert_level", "info")
            if level in ["critical", "warning"] or z.density > 70:
                alerts.append(Alert(zone=z.zone, level="critical" if z.density > 90 else level, message=ai_res["message"]))
            recommendations.append(Recommendation(action=f"AI System [{z.zone}]", reason=ai_res["recommendation"]))
            
        if not handled:
            if z.density > 90:
                alerts.append(Alert(zone=z.zone, level="critical", message=f"Critical overcrowding near {z.zone}. Immediate rerouting required."))
            elif z.density > 70:
                alerts.append(Alert(zone=z.zone, level="warning", message=f"Heavy crowd near {z.zone}. Expect delays."))
                
            if z.density < 30:
                 recommendations.append(Recommendation(action=f"Move to {z.zone}", reason="Safe zone available. Recommended for movement."))
             
    if not recommendations:
        recommendations.append(Recommendation(action="Stay alert", reason="All venue locations reporting elevated densities."))
        
    return InsightsResponse(alerts=alerts, recommendations=recommendations)

async def evaluate_alerts(zones: List[ZoneDensity], event_type: EventType = EventType.F1) -> List[Alert]:
    insights = await evaluate_insights(zones, event_type)
    return insights.alerts

 
