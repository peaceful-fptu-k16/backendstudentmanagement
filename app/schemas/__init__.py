from typing import Generic, TypeVar, List, Optional
from sqlmodel import SQLModel

T = TypeVar('T')

class PaginatedResponse(SQLModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool

class AnalyticsResponse(SQLModel):
    """Analytics response schema"""
    total_students: int
    average_scores: dict
    score_distribution: dict
    hometown_distribution: dict
    grade_distribution: dict
    subject_comparison: dict

class ExportRequest(SQLModel):
    """Export request schema"""
    format: str = "csv"  # csv, excel, xml
    filters: Optional[dict] = None
    include_analytics: bool = False

class CrawlRequest(SQLModel):
    """Crawl request schema"""
    url: str
    parse_type: str = "student_list"  # student_list, single_student
    output_format: str = "excel"  # excel, csv, json

class GenerateReportRequest(SQLModel):
    """Generate report request schema from frontend"""
    current_url: str
    frontend_base_url: str
    timestamp: str