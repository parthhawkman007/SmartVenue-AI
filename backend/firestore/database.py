from google.cloud import firestore
import logging
import firebase_admin

logger = logging.getLogger(__name__)

try:
    if not firebase_admin._apps:
        firebase_admin.initialize_app()
    # Execution relies on Google Application Default Credentials (ADC)
    db = firestore.AsyncClient()
    logger.info("Firestore async client initialized")
except Exception as e:
    db = None
    logger.warning("Firestore init failed, using fallback memory state: %s", e)

async def get_db():
    return db

async def is_system_active() -> bool:
    if not db:
        return True
    try:
        doc = await db.collection("system_state").document("global").get()
        if doc.exists:
            return doc.to_dict().get("active", False)
        return False
    except Exception:
        return False

async def setup_database():
    """Seed Firestore with baseline venue data when the collection is empty."""
    from ..models.schemas import ZoneDensity, EventType
    if db is not None:
        try:
            docs = [doc async for doc in db.collection("crowd_data").limit(1).stream()]
            if not docs:
                samples = [
                    ZoneDensity(zone="Main Entrance", density=85, status="Very Crowded", event_type=EventType.F1),
                    ZoneDensity(zone="Food Court", density=60, status="Moderate", event_type=EventType.F1),
                    ZoneDensity(zone="Restrooms", density=15, status="Low", event_type=EventType.F1),
                    ZoneDensity(zone="VIP Lounge", density=5, status="Low", event_type=EventType.F1),
                    ZoneDensity(zone="Stage Area A", density=98, status="Very Crowded", event_type=EventType.F1)
                ]
                for s in samples:
                    doc_data = s.model_dump()
                    doc_data["source"] = "firestore"
                    await db.collection("crowd_data").document(s.zone).set(doc_data)
                logger.info("Firestore crowd_data collection seeded with sample data")
        except Exception as e:
            logger.warning("Failed to seed Firestore crowd_data collection: %s", e)
