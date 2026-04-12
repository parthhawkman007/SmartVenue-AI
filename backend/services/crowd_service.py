import random
from typing import List, Dict
from models.schemas import ZoneDensity, InsightsResponse, Alert, Recommendation

# Global state to maintain previous values per zone persistently in RAM mapped to Cloud Run instances natively
PREVIOUS_DENSITY: Dict[str, int] = {}

def map_zone_names(zone: str, event_type: str) -> str:
    """Translates generic database zones into localized physical stadium architectures."""
    if event_type.lower() == "football":
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
from services.gemini_service import generate_insight_async

async def evaluate_insights(zones: List[ZoneDensity], event_type: str = "F1") -> InsightsResponse:
    """Orchestrator Intelligence Engine natively invoking Gemini parameters and structured caching bounds."""
    alerts = []
    recommendations = []
    
    # Strictly parallelize API queries completely dodging execution bottlenecks directly
    tasks = [generate_insight_async(z.zone, z.density, z.trend, event_type) for z in zones]
    gemini_responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    for z, ai_res in zip(zones, gemini_responses):
        handled = False
        
        # Native AI processing cleanly tracked securely
        if isinstance(ai_res, dict):
            handled = True
            level = ai_res.get("alert_level", "info")
            if level in ["critical", "warning"] or z.density > 70:
                alerts.append(Alert(zone=z.zone, level="critical" if z.density > 90 else level, message=ai_res["message"]))
            recommendations.append(Recommendation(action=f"AI Structural Optimization [{z.zone}]", reason=ai_res["recommendation"]))
            
        # Physical Core Logic bounding completely overriding timeouts cleanly!
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

async def evaluate_alerts(zones: List[ZoneDensity], event_type: str = "F1") -> List[Alert]:
    insights = await evaluate_insights(zones, event_type)
    return insights.alerts

def generate_simulated_data(event: str = "F1") -> List[ZoneDensity]:
    """Generates jittered simulated payloads perfectly reflecting physical environments.
    
    INTEGRATION PIPELINE DOCUMENTATION
    ==================================
    In a real-world stadium or track architecture, this mock generator endpoint is entirely 
    bypassed. External large-scale IoT edge clusters orchestrate data ingestion via:
     - 📷 Computer Vision Models mapping camera feeds into bounding-box density aggregates.
     - 🎟 RFID Turnstile gateways calculating raw Entry versus Exit diff bounds dynamically.
     - 📶 Dense WiFi Access Point tracking logging unique MAC connections isolated per cluster.
    This pipeline drives real-time analytics pushing natively to the POST /crowd gateway!
    """
    base_zones = ["Main Entrance", "Food Court", "Restrooms", "VIP Lounge", "Stage Area A"]
    event_lb = event.lower()
    
    zones = []
    for base_z in base_zones:
        # Simulate highly accurate contextual domain spikes!
        if event_lb == "f1" and base_z in ["Main Entrance", "Stage Area A"]: # Race Start Surge / Pit Walk
            base_density = random.randint(85, 98)
        elif event_lb == "football" and base_z in ["Food Court", "Restrooms"]: # Football Halftime Rush
            base_density = random.randint(80, 95)
        else:
            base_density = PREVIOUS_DENSITY.get(base_z, random.randint(15, 60))
            
        # Add pure noise tracking realistic movement patterns natively
        new_density = max(0, min(100, base_density + random.randint(-15, 15)))
        
        status = "Low"
        if new_density > 90: status = "Very Crowded"
        elif new_density > 70: status = "Crowded"
        elif new_density > 30: status = "Moderate"
        
        zones.append(ZoneDensity(
            zone=base_z, # Return base to allow routers to natively translate and memory map dynamically
            density=new_density,
            status=status,
            source="simulation",
            event_type=event
        ))
    return zones
