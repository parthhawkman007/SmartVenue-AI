from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.auth import require_admin
from firestore.database import get_db
import datetime

class RoleUpdateRequest(BaseModel):
    uid: str
    action: str

router = APIRouter(prefix="/admin", tags=["Admin Controls"])

@router.post("/system/start")
async def start_system(event_type: str = "F1", user: dict = Depends(require_admin)):
    db = await get_db()
    if db:
        await db.collection("system_state").document("global").set({
            "active": True,
            "event_type": event_type,
            "started_by": user["uid"],
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        })
    return {"status": "success", "message": f"System actively engaged mapping '{event_type}' seamlessly!"}

@router.post("/system/stop")
async def stop_system(user: dict = Depends(require_admin)):
    db = await get_db()
    if db:
        await db.collection("system_state").document("global").set({
            "active": False,
            "stopped_by": user["uid"],
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }, merge=True)
    return {"status": "success", "message": "System disengaged safely!"}

@router.post("/users/role")
async def update_user_role(payload: RoleUpdateRequest, user: dict = Depends(require_admin)):
    db = await get_db()
    if not db:
        raise HTTPException(status_code=500, detail="Database securely locked.")
        
    target_uid = payload.uid
    action = payload.action
    
    # Critical self-demotion protection securely bounded natively
    if target_uid == user["uid"] and action == "demote":
        raise HTTPException(status_code=400, detail="Admins cannot logically demote themselves without transferring root.")
        
    doc_ref = db.collection("users").document(target_uid)
    doc_snap = await doc_ref.get()
    
    if not doc_snap.exists:
        raise HTTPException(status_code=404, detail="Target user not found.")
        
    # Prevent structural lockout (Cannot demote the final operating Admin)
    if action == "demote":
        admins_query = db.collection("users").where("role", "==", "admin")
        admins = await admins_query.get()
        if len(admins) <= 1:
            raise HTTPException(status_code=400, detail="Cannot cleanly drop the final administrative instance!")
            
    # Commit native change
    new_role = "admin" if action == "promote" else "user"
    await doc_ref.update({"role": new_role})
    
    return {"status": "success", "message": f"Successfully mapped identity parameter natively to {new_role}."}
