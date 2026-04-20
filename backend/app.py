from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import time

from routes import crowd, insights, alerts, environment, admin
from models.schemas import success_response, error_response
from firestore.database import db, setup_database
from contextlib import asynccontextmanager

from core.config import settings

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Production-ready scalable Crowd Management intelligence system.",
    version=settings.VERSION,
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Secure logging middleware tracking API performance."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        "API request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "duration_seconds": round(process_time, 4),
            "status_code": response.status_code,
        },
    )
    return response

from fastapi.responses import JSONResponse
import datetime
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    status_code = getattr(exc, "status_code", 500)
    detail = getattr(exc, "detail", "An internal server error occurred.")
    return JSONResponse(status_code=status_code, content=error_response(str(detail)))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content=error_response(str(exc.detail)))

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content=error_response("Data validation logically failed"))
@app.get("/")
async def root():
    return success_response({"service": settings.PROJECT_NAME, "version": settings.VERSION}, "System is online.")

# Connect Modulated Fast API Routers natively
app.include_router(crowd.router, tags=["Crowd Streams"])
app.include_router(insights.router, tags=["Intelligence & Recommendations"])
app.include_router(alerts.router, tags=["Watchdog Alerts"])
app.include_router(environment.router, tags=["Structural Environment"])
app.include_router(admin.router)

 
@app.get("/health")
async def health_check():
    return success_response({"service": settings.PROJECT_NAME}, "Service is healthy")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=settings.DEFAULT_PORT, reload=False)
