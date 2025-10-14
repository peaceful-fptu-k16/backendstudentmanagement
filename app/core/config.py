import os
from typing import Optional

class Settings:
    DATABASE_URL: str = "sqlite:///./students.db"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Student Management API"
    PROJECT_VERSION: str = "1.0.0"
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024
    CACHE_TTL: int = 300
    ENABLE_BACKGROUND_TASKS: bool = True
    EXPORT_BATCH_SIZE: int = 1000
    CRAWLER_USER_AGENT: str = "Student Management Crawler 1.0"
    CRAWLER_DELAY: float = 1.0
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5500",
    ]
    
    def __init__(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

settings = Settings()
