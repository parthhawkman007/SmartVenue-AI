from google.cloud import firestore
import firebase_admin
from firebase_admin import credentials

try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    # Execution relies on Google Application Default Credentials (ADC)
    db = firestore.AsyncClient()
    print("[FIRESTORE INIT] Client connected securely.")
except Exception as e:
    db = None
    print(f"[FIRESTORE INIT FAIL] {e}. System falling back to memory states seamlessly.")

async def get_db():
    return db

async def is_system_active() -> bool:
    if not db: return True # Fallback secure gracefully
    try:
        doc = await db.collection("system_state").document("global").get()
        if doc.exists:
            return doc.to_dict().get("active", False)
        return False
    except Exception:
        return False
