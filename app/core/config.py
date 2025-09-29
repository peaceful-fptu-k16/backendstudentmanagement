import os
from typing import Optional

class Settings:
    # Database
    DATABASE_URL: str = "sqlite:///./students.db"
    
    # API
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Student Management API"
    PROJECT_VERSION: str = "1.0.0"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Cache
    CACHE_TTL: int = 300  # 5 minutes
    
    # Background tasks
    ENABLE_BACKGROUND_TASKS: bool = True
    
    # Export settings
    EXPORT_BATCH_SIZE: int = 1000
    
    # Crawler settings
    CRAWLER_USER_AGENT: str = "Student Management Crawler 1.0"
    CRAWLER_DELAY: float = 1.0  # seconds between requests
    
    def __init__(self):
        # Create upload directory if it doesn't exist
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

settings = Settings()