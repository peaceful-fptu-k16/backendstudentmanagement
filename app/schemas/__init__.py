from sqlmodel import SQLModel

class AnalyticsResponse(SQLModel):
    total_students: int
    average_scores: dict
    score_distribution: dict
    hometown_distribution: dict
    grade_distribution: dict
    subject_comparison: dict

class CrawlRequest(SQLModel):
    url: str
    parse_type: str = "student_list"
    output_format: str = "excel"

class GenerateReportRequest(SQLModel):
    current_url: str
    frontend_base_url: str
    timestamp: str