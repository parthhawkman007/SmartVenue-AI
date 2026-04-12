import os
import time
import asyncio
import google.generativeai as genai
from typing import Optional, Dict, Tuple

# Pure in-memory cache natively tracking hash strings for exact execution bounds
# Shape: { (zone, trend, event_type, rounded_density): (timestamp, payload_dict) }
GEMINI_CACHE: Dict[Tuple[str, str, str, int], Tuple[float, dict]] = {}
CACHE_TTL = 300 # Expiration structurally set at 5 minutes to prevent stale drift

# Safe Configuration mapping securely preserving system startup integrity if key is absent natively
gemini_api_key = os.environ.get("GEMINI_API_KEY")
if gemini_api_key:
    genai.configure(api_key=gemini_api_key)

# Bind the most heavily optimized native flash architecture Model
model = genai.GenerativeModel('gemini-1.5-flash')

async def generate_insight_async(zone: str, density: int, trend: str, event_type: str) -> Optional[dict]:
    """Generates structural JSON outputs natively bypassing latency strictly using local memory hashing caches."""
    # Round density to nearest 5 bounds aggressively clamping cache execution requests saving raw quotas
    rounded_density = 5 * round(density / 5)
    cache_key = (zone, trend, event_type, rounded_density)
    
    current_time = time.time()
    
    # 1. Native Cache Intercept
    if cache_key in GEMINI_CACHE:
        timestamp, cached_data = GEMINI_CACHE[cache_key]
        if current_time - timestamp < CACHE_TTL:
            return cached_data
            
    # 2. Escape Fallback securely preventing trace explosions if API drops!
    if not gemini_api_key:
        return None
        
    prompt = f"""
You are an intelligent crowd management assistant for a {event_type} event.
Given:
Zone: {zone}
Density: {density}%
Trend: {trend}

Please generate exactly three lines of clean text smoothly. Remove all bullet points, markup, or asterisks.
Line 1: Return ONLY the severity level: 'critical' if density > 90, 'warning' if density > 70, or 'info' otherwise.
Line 2: A highly professional operational alert referencing the zone metrics structurally.
Line 3: An intelligent actionable recommendation for stadium control nodes dynamically.
"""
    
    try:
        # Heavily restricted bounding tracking strictly catching failures under 3000ms thresholds
        response = await asyncio.wait_for(
            model.generate_content_async(prompt),
            timeout=2.8
        )
        
        lines = [l.replace("-", "").replace("*", "").strip() for l in response.text.split("\n") if l.strip()]
        
        if len(lines) >= 3:
            level = lines[0].lower()
            if level not in ["critical", "warning", "info"]:
                level = "warning" if density > 70 else "info"
                
            payload = {
                "alert_level": level,
                "message": lines[1],
                "recommendation": lines[2]
            }
            
            # Persist structurally immediately into RAM caches mitigating heavy API execution intervals
            GEMINI_CACHE[cache_key] = (current_time, payload)
            return payload
            
    except Exception as e:
        print(f"[GEMINI AI TRACE] Execution gracefully bypassed generating structural fallback logic natively: {e}")
        
    return None
