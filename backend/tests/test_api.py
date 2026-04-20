"""
SmartVenue AI - Production-Grade Backend Test Suite
Validates critical API endpoints with authentication mocking.
"""
import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from services.auth import get_current_user, require_admin

# --- MOCK CONTEXT ---
async def mock_get_current_user():
    return {
        "uid": "test_user_123",
        "email": "test@example.com",
        "role": "admin"
    }

async def mock_is_system_active():
    return True

import unittest.mock
# Patch across the relevant modules
patcher1 = unittest.mock.patch('routes.environment.is_system_active', new=mock_is_system_active)
patcher2 = unittest.mock.patch('routes.crowd.is_system_active', new=mock_is_system_active)
patcher3 = unittest.mock.patch('routes.alerts.is_system_active', new=mock_is_system_active)
patcher4 = unittest.mock.patch('routes.insights.is_system_active', new=mock_is_system_active)

patcher1.start()
patcher2.start()
patcher3.start()
patcher4.start()

app.dependency_overrides[get_current_user] = mock_get_current_user
app.dependency_overrides[require_admin] = mock_get_current_user

client = TestClient(app)

def assert_schema(data: dict):
    """Validates structural Base API schema compliance."""
    assert "status" in data
    assert "message" in data
    assert "timestamp" in data
    assert "data" in data

# --- TEST SUITE ---

def test_root_endpoint():
    """CRITICAL: Validates the root heartbeat endpoint format."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert_schema(data)
    assert data["status"] == "success"
    assert data["data"]["service"] == "SmartVenue AI Intelligence Engine"

def test_health_check_endpoint():
    """Validates legacy health endpoint structural compliances."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert_schema(data)
    assert data["status"] == "success"

async def mock_get_current_user_standard():
    return {
        "uid": "test_user_789",
        "email": "standard@example.com",
        "role": "user"
    }

def test_unauthorized_access():
    """Edge Case: Ensure missing credentials return error wrapper naturally."""
    # Temporarily remove override
    app.dependency_overrides = {}
    response = client.get("/alerts")
    # Missing Auth raises 401
    assert response.status_code == 401
    assert_schema(response.json())
    assert response.json()["status"] == "error"
    # Restore overrides natively
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_admin] = mock_get_current_user

def test_forbidden_admin_access():
    """Validates user hitting admin endpoints drops to proper 403 mapping safely."""
    # Override with standard user temporarily natively
    app.dependency_overrides[get_current_user] = mock_get_current_user_standard
    if require_admin in app.dependency_overrides:
        del app.dependency_overrides[require_admin]
        
    response = client.post("/admin/system/start?event_type=F1")
    assert response.status_code == 403
    assert_schema(response.json())
    assert response.json()["status"] == "error"
    
    # Restore overrides natively
    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_admin] = mock_get_current_user

def test_forbidden_crowd_write_for_standard_user():
    """Validates only admins can write crowd density updates."""
    app.dependency_overrides[get_current_user] = mock_get_current_user_standard
    if require_admin in app.dependency_overrides:
        del app.dependency_overrides[require_admin]

    response = client.post(
        "/crowd",
        json={"zone": "Gate B", "density": 55, "status": "Moderate"}
    )
    assert response.status_code == 403
    assert_schema(response.json())
    assert response.json()["status"] == "error"

    app.dependency_overrides[get_current_user] = mock_get_current_user
    app.dependency_overrides[require_admin] = mock_get_current_user

@unittest.mock.patch('routes.admin.get_db', new_callable=unittest.mock.AsyncMock)
def test_firestore_interaction_mocked(mock_get_db):
    """Mocks Firebase to ensure gracefully handled isolated persistence layers natively without crashes."""
    # Simulate DB disconnection
    mock_get_db.return_value = None
    
    response = client.post("/admin/system/start?event_type=F1")
    # If DB is None, the admin endpoint cleanly raises 500 error wrapper natively
    assert response.status_code == 500
    assert_schema(response.json())
    assert response.json()["status"] == "error"

def test_invalid_input_edge_case():
    """Edge Case: Ensure Pydantic validations bubble out cleanly through Global Exception Handler."""
    # Posting mismatched schemas to enforce cleanly caught internal failures!
    response = client.post("/crowd", json={"zone": "TooShort"})
    assert response.status_code == 422
    data = response.json()
    assert_schema(data)
    assert data["status"] == "error"

def test_invalid_role_action_rejected():
    """Invalid admin role actions should fail schema validation."""
    response = client.post("/admin/users/role", json={"uid": "user_123", "action": "delete"})
    assert response.status_code == 422
    assert_schema(response.json())
    assert response.json()["status"] == "error"

@unittest.mock.patch("routes.admin.auth.revoke_refresh_tokens")
@unittest.mock.patch("routes.admin.auth.set_custom_user_claims")
@unittest.mock.patch("routes.admin.auth.get_user")
def test_role_update_sets_custom_claims(mock_get_user, mock_set_claims, mock_revoke_tokens):
    """Admin role updates should write Firebase custom claims and revoke old sessions."""
    mock_get_user.return_value = object()

    response = client.post("/admin/users/role", json={"uid": "user_123", "action": "promote"})

    assert response.status_code == 200
    payload = response.json()
    assert_schema(payload)
    assert payload["data"]["new_role"] == "admin"
    mock_set_claims.assert_called_once_with("user_123", {"role": "admin"})
    mock_revoke_tokens.assert_called_once_with("user_123")

def test_integration_flow_sequence():
    """Light Integration Flow: Validates sequence environment -> crowd -> alerts -> insights"""
    
    # Force system active for flow test to prevent 503 idle drop
    start_resp = client.post("/admin/system/start?event_type=F1")
    assert start_resp.status_code == 200
    
    # 1. Environment
    env_res = client.get("/environment?event=F1")
    assert env_res.status_code == 200
    assert_schema(env_res.json())
    assert "event_phase" in env_res.json()["data"]
    
    # 2. Crowd Sim
    crowd_res = client.get("/simulate?event=F1")
    assert crowd_res.status_code == 200
    assert_schema(crowd_res.json())
    assert isinstance(crowd_res.json()["data"], list)
    
    # 3. Alerts
    alerts_res = client.get("/alerts?event=F1")
    assert alerts_res.status_code == 200
    assert_schema(alerts_res.json())
    
    # 4. Insights
    insights_res = client.get("/insights?event=F1")
    assert insights_res.status_code == 200
    assert_schema(insights_res.json())

if __name__ == "__main__":
    pytest.main([__file__])
