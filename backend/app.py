from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import time

from routes import crowd, insights, alerts, environment, admin
from models.schemas import ZoneDensity, HealthResponse
from firestore.database import db

app = FastAPI(
    title="SmartVenue AI Intelligence Engine",
    description="Production-ready scalable Crowd Management intelligence system."
)

ALLOWED_ORIGINS = [
    "https://smart-experience-ai.web.app",
    "http://localhost:5000",
    "http://127.0.0.1:5000",
    "http://localhost:5500",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Secure logging middleware tracking speed cleanly avoiding sensitive data."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    print(f"[API] {request.method} {request.url.path} - executed in {process_time:.4f}s")
    return response

from fastapi.responses import JSONResponse
import datetime

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """High-security Global Exception mapping to secure abstract JSON schemas systematically."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "An internal server error occurred.", # obfuscate actual exception
            "type": type(exc).__name__,
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
    )

# Connect Modulated Fast API Routers natively
app.include_router(crowd.router, tags=["Crowd Streams"])
app.include_router(insights.router, tags=["Intelligence & Recommendations"])
app.include_router(alerts.router, tags=["Watchdog Alerts"])
app.include_router(environment.router, tags=["Structural Environment"])
app.include_router(admin.router)

@app.on_event("startup")
async def setup():
    if db is not None:
        try:
            docs = [doc async for doc in db.collection("crowd_data").limit(1).stream()]
            if not docs:
                samples = [
                    ZoneDensity(zone="Main Entrance", density=85, status="Very Crowded"),
                    ZoneDensity(zone="Food Court", density=60, status="Moderate"),
                    ZoneDensity(zone="Restrooms", density=15, status="Low"),
                    ZoneDensity(zone="VIP Lounge", density=5, status="Low"),
                    ZoneDensity(zone="Stage Area A", density=98, status="Very Crowded")
                ]
                for s in samples:
                    doc_data = s.model_dump()
                    doc_data["source"] = "firestore"
                    await db.collection("crowd_data").document(s.zone).set(doc_data)
        except Exception as e:
            print(f"[INIT ERROR] Failed automatic DB seeding: {e}")

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Validation API health endpoint exposed natively matching structural compliances."""
    return HealthResponse(
        status="ok", 
        service="Smart Experience AI",
        timestamp=datetime.datetime.utcnow().isoformat() + "Z"
    )

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=False)
