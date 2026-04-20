from fastapi import APIRouter, Depends, HTTPException
from typing import Optional
from typing import Any
import logging

from ..models.schemas import APIResponse, RoleAction, RoleUpdateRequest, success_response, EventType
from ..services.auth import require_admin
from ..firestore.database import get_db
from firebase_admin import auth
import datetime

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin Controls"])

@router.post("/system/start", response_model=APIResponse[dict])
async def start_system(
    event_type: EventType = EventType.F1,
    event: Optional[EventType] = None,
    user: dict = Depends(require_admin),
) -> Any:
    """Activates the global intelligence processing engine for a specific event domain."""
    db = await get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database instance unavailable.")

    selected_event = event or event_type
        
    await db.collection("system_state").document("global").set({
        "active": True,
        "event_type": selected_event.value,
        "started_by": user["uid"],
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    })
    return success_response(None, f"System creatively engaged mapping '{selected_event.value}'")

@router.post("/system/stop", response_model=APIResponse[dict])
async def stop_system(user: dict = Depends(require_admin)) -> Any:
    """Gracefully halts the active processing engine into IDLE modes."""
    db = await get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database instance unavailable.")
        
    await db.collection("system_state").document("global").set({
        "active": False,
        "stopped_by": user["uid"],
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
    }, merge=True)
    return success_response(None, "System disengaged safely")

@router.post("/users/role", response_model=APIResponse[dict])
async def update_user_role(payload: RoleUpdateRequest, user: dict = Depends(require_admin)) -> Any:
    """Manipulates administrative custom claims globally."""
    target_uid = payload.uid
    action = payload.action
    
    if target_uid == user["uid"] and action == RoleAction.DEMOTE:
        raise HTTPException(status_code=400, detail="Admins cannot demote themselves.")
        
    try:
        auth.get_user(target_uid)
    except auth.UserNotFoundError:
        logger.warning("Role update requested for missing user '%s'", target_uid)
        raise HTTPException(status_code=404, detail="Target user not found.")
    except Exception:
        logger.exception("Unable to load Firebase user '%s'", target_uid)
        raise HTTPException(status_code=500, detail="Unable to load target user.")
        
    new_role = "admin" if action == RoleAction.PROMOTE else "user"
    auth.set_custom_user_claims(target_uid, {"role": new_role})
    auth.revoke_refresh_tokens(target_uid)
    
    return success_response({"new_role": new_role}, f"Successfully mapped role to {new_role}")
