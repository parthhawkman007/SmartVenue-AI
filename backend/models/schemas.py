import datetime
from typing import List, Optional, TypeVar, Generic, Any
from pydantic import BaseModel, Field
from enum import Enum

T = TypeVar('T')

class EventType(str, Enum):
    F1 = "F1"
    FOOTBALL = "Football"


class RoleAction(str, Enum):
    PROMOTE = "promote"
    DEMOTE = "demote"

class APIResponse(BaseModel, Generic[T]):
    """Standardized API Response wrapper guaranteeing structural consistency."""
    status: str = Field(..., description="'success' or 'error'")
    data: Optional[T] = None
    message: str = Field(..., description="Human readable message")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")

def success_response(data: Any, message: str = "Success") -> dict:
    return {"status": "success", "data": data, "message": message, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"}

def error_response(message: str) -> dict:
    return {"status": "error", "data": None, "message": message, "timestamp": datetime.datetime.utcnow().isoformat() + "Z"}

class ZoneDensity(BaseModel):
    """Core Pydantic Schema mapping active Crowd parameters"""
    zone: str = Field(..., min_length=2, max_length=50)
    density: int = Field(..., ge=0, le=100)
    status: str = Field(..., min_length=2, max_length=20)
    trend: str = Field(default="stable", description="Trend direction: increasing, decreasing, or stable")
    timestamp: str = Field(default_factory=lambda: datetime.datetime.utcnow().isoformat() + "Z")
    source: str = Field(default="fallback")
    event_type: EventType = Field(default=EventType.F1, description="Sporting context (F1 or Football)")

class Alert(BaseModel):
    zone: str
    level: str
    message: str

class Recommendation(BaseModel):
    action: str
    reason: str


class RoleUpdateRequest(BaseModel):
    uid: str = Field(..., min_length=1)
    action: RoleAction

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
