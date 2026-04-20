import os
from typing import List

class Settings:
    PROJECT_NAME: str = "SmartVenue AI Intelligence Engine"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Firestore / Auth
    FIREBASE_CREDENTIALS: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
    
    # Security/CORS
    ALLOWED_ORIGINS: List[str] = [
        "https://smart-experience-ai.web.app",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://localhost:5500",
        "http://127.0.0.1:5500"
    ]
    
    # Defaults
    DEFAULT_EVENT_TYPE: str = "F1"
    DEFAULT_PORT: int = int(os.environ.get("PORT", 8080))
    
    # Roles
    ROLE_ADMIN: str = "admin"
    ROLE_USER: str = "user"

settings = Settings()
