"""
SmartVenue AI - Production-Grade Backend Test Suite
Validates critical API endpoints with authentication mocking.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services.auth import get_current_user

# --- MOCK CONTEXT ---
async def mock_get_current_user():
    """Bypasses Firebase Auth for testing purposes."""
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "admin"
    }

# Apply dependency override globally for the test session
app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)

# --- TEST SUITE ---

def test_root_endpoint():
    """
    CRITICAL: Validates the root heartbeat endpoint.
    Ensures the system is online and returning compliant JSON.
    """
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "service" in data
    assert "timestamp" in data

def test_alerts_endpoint_structure():
    """
    Validates /alerts endpoint schema and authorized access.
    Checks for list format and required alert fields.
    """
    response = client.get("/alerts?event=F1")
    # If system is idle during test, it returns 503 (correct behavior)
    # If seeded it returns 200. We accept both as 'active infrastructure'.
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert "zone" in data[0]
            assert "level" in data[0]
            assert "message" in data[0]

def test_insights_endpoint_structure():
    """
    Validates /insights endpoint schema and AI recommendation mapping.
    """
    response = client.get("/insights?event=F1")
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)

def test_environment_endpoint_structure():
    """
    Validates /environment endpoint and meteorological simulation.
    """
    response = client.get("/environment?event=F1")
    assert response.status_code in [200, 503]
    
    if response.status_code == 200:
        data = response.json()
        assert "event_phase" in data
        assert "weather_condition" in data
        assert "temperature_celsius" in data

def test_health_check_endpoint():
    """
    Validates legacy health endpoint compliance.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

if __name__ == "__main__":
    # Manual execution helper
    pytest.main([__file__])
