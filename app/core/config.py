"""
Application Configuration Settings

This module contains all configuration settings for the Student Management API.
Includes database, API, pagination, upload, cache, and crawler configurations.
Settings are loaded from environment variables or use default values.
"""

import os
from typing import Optional

class Settings:
    """
    Application settings and configuration
    
    All settings can be overridden via environment variables.
    Default values are provided for development environment.
    """
    
    # ============================================================================
    # Database Configuration
    # ============================================================================
    DATABASE_URL: str = "sqlite:///./students.db"  # SQLite database file path
    
    # ============================================================================
    # API Configuration
    # ============================================================================
    API_V1_STR: str = "/api/v1"  # API version prefix for all endpoints
    PROJECT_NAME: str = "Student Management API"  # Project display name
    PROJECT_VERSION: str = "1.0.0"  # Current API version
    
    # ============================================================================
    # Pagination Settings
    # ============================================================================
    DEFAULT_PAGE_SIZE: int = 20  # Default number of items per page
    MAX_PAGE_SIZE: int = 100  # Maximum allowed items per page
    
    # ============================================================================
    # File Upload Settings
    # ============================================================================
    UPLOAD_DIR: str = "uploads"  # Directory for uploaded files
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # Maximum file size: 10MB
    
    # ============================================================================
    # Cache Settings
    # ============================================================================
    CACHE_TTL: int = 300  # Cache time-to-live in seconds (5 minutes)
    
    # ============================================================================
    # Background Task Settings
    # ============================================================================
    ENABLE_BACKGROUND_TASKS: bool = True  # Enable/disable async background tasks
    
    # ============================================================================
    # Export Settings
    # ============================================================================
    EXPORT_BATCH_SIZE: int = 1000  # Number of records to process per batch
    
    # ============================================================================
    # Web Crawler Settings
    # ============================================================================
    CRAWLER_USER_AGENT: str = "Student Management Crawler 1.0"  # User-Agent header
    CRAWLER_DELAY: float = 1.0  # Delay in seconds between consecutive requests
    
    # ============================================================================
    # CORS Settings
    # ============================================================================
    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5500",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5500",
    ]  # Allowed origins for CORS
    
    def __init__(self):
        """
        Initialize settings and create required directories
        
        Creates the upload directory if it doesn't exist.
        """
        # Ensure upload directory exists for file uploads
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

# Global settings instance for application-wide access
settings = Settings()
