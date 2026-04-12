"""
SmartVenue AI - Pytest Backend Suite
"""
import sys
import os
from unittest.mock import patch

from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = TestClient(app)

def test_get_crowd_returns_list():
    """Validates that the crowd endpoint rigorously returns an instantiated list schema mapping zones."""
    response = client.get("/crowd")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # The hybrid architecture drops into static fallback natively avoiding mock setups entirely
    assert len(data) > 0
    assert "zone" in data[0]
    assert "density" in data[0]

def test_get_insights_returns_schema():
    """Ensures insights engine intelligently triggers analytical fields."""
    response = client.get("/insights")
    assert response.status_code == 200
    data = response.json()
    
    # Validations matching strict structural requirements natively
    assert "alerts" in data
    assert "recommendations" in data
    assert isinstance(data["alerts"], list)
    assert isinstance(data["recommendations"], list)

def test_health_check_compliant():
    """Confirms production health metrics yield compliant objects globally."""
    response = client.get("/health")
    assert response.status_code == 200
    expected = response.json()
    assert expected["status"] == "ok"
    assert "service" in expected
    assert "timestamp" in expected
