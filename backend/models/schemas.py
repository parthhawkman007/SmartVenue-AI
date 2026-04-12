import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ZoneDensity(BaseModel):
    """Core Pydantic Schema mapping active Crowd parameters"""
    zone: str = Field(..., min_length=2, max_length=50)
    density: int = Field(..., ge=0, le=100)
    status: str = Field(..., min_length=2, max_length=20)
    trend: str = Field(default="stable", description="Trend direction: increasing, decreasing, or stable")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    source: str = Field(default="fallback")
    event_type: str = Field(default="F1", description="Sporting context (Formula1 or Football)")

class Alert(BaseModel):
    zone: str
    level: str
    message: str

class Recommendation(BaseModel):
    action: str
    reason: str

class InsightsResponse(BaseModel):
    """Encapsulates Critical Alerts and Tactical Recommendations dynamically"""
    alerts: List[Alert]
    recommendations: List[Recommendation]

class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: str

class EnvironmentResponse(BaseModel):
    event_phase: str
    weather_condition: str
    temperature_celsius: int
    humidity_percent: int
