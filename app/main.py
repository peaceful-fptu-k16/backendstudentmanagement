from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import time
import traceback

from app.core.config import settings
from app.database import create_db_and_tables
from app.api import api_router
from app.core.logging import get_api_logger, get_structured_logger, StudentManagementLogger

log_manager = StudentManagementLogger()
logger = get_api_logger()
structured_logger = get_structured_logger("api")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description="Backend API for Student Management System",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    structured_logger.log_api_request(
        method=request.method,
        path=str(request.url.path),
        remote_addr=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent")
    )
    
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    response.headers["X-Process-Time"] = str(process_time)
    
    structured_logger.log_api_response(
        method=request.method,
        path=str(request.url.path),
        status_code=response.status_code,
        duration=process_time,
        response_size=response.headers.get("content-length")
    )
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s - "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )
    
    return response
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    error_trace = traceback.format_exc()
    structured_logger.log_error(
        error_type=type(exc).__name__,
        error_message=str(exc),
        stack_trace=error_trace,
        context={
            "method": request.method,
            "path": str(request.url.path),
            "remote_addr": request.client.host if request.client else "unknown"
        }
    )
    
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {str(exc)}")
    logger.error(f"Stack trace: {error_trace}")
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__,
            "timestamp": time.time()
        }
    )

app.include_router(api_router, prefix=settings.API_V1_STR)
@app.get("/")
async def root():
    return {
        "message": "Student Management System API",
        "version": settings.PROJECT_VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_prefix": settings.API_V1_STR
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": settings.PROJECT_VERSION
    }

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Student Management API...")
    log_manager.cleanup_old_logs(days_to_keep=30)
    logger.info(f"Log cleanup completed - current log folder: {log_manager.get_current_log_folder()}")
    create_db_and_tables()
    logger.info("Database tables created/verified")
    logger.info("API startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down Student Management API...")
    logger.info("API shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )