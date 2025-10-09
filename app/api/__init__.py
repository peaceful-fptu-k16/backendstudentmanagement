from fastapi import APIRouter
from .endpoints import students, analytics, export, crawler, visualizations, html_crawler

api_router = APIRouter()

api_router.include_router(students.router, prefix="/students", tags=["students"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(crawler.router, prefix="/crawler", tags=["crawler"])
api_router.include_router(visualizations.router, prefix="/visualizations", tags=["visualizations"])
api_router.include_router(html_crawler.router, tags=["html-crawler"])