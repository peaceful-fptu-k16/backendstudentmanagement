from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from sqlmodel import Session

from app.core.dependencies import get_db
from app.schemas import CrawlRequest
from app.services.crawler_service import CrawlerService
from app.services.data_service import DataService
from app.services.report_generator_service import report_generator
from app.crud.student import student_crud
from app.models.student import StudentBulkImportResult, Student

router = APIRouter()

@router.post("/crawl", response_model=Dict[str, Any])
async def crawl_website(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crawl student data from a website and generate comprehensive report"""
    
    try:
        crawler = CrawlerService()
        
        if crawl_request.parse_type == "auto":
            # Auto-detect student data
            raw_data = crawler.auto_detect_student_data(crawl_request.url)
        elif crawl_request.parse_type == "student_list":
            # Parse as student list table
            raw_data = crawler.crawl_student_list(crawl_request.url)
        elif crawl_request.parse_type == "single_student":
            # Parse as single student detail page
            student_data = crawler.crawl_student_detail(crawl_request.url)
            raw_data = [student_data] if student_data else []
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parse_type. Use 'auto', 'student_list', or 'single_student'"
            )
        
        # If no data found, return informative response instead of 404
        if not raw_data:
            return {
                "success": False,
                "message": "No student data found on the webpage",
                "crawl_url": crawl_request.url,
                "parse_type": crawl_request.parse_type,
                "found_students": 0,
                "valid_students": 0,
                "suggestions": [
                    "Check if the URL is correct and accessible",
                    "Try a different parse_type (auto, student_list, or single_student)",
                    "Ensure the webpage contains student data in a recognizable format",
                    "Use /test-crawl endpoint to preview the data structure"
                ]
            }
        
        # Clean and validate data
        students_data = crawler.clean_crawled_data(raw_data)
        
        if not students_data:
            return {
                "success": False,
                "message": "No valid student data could be extracted after cleaning",
                "crawl_url": crawl_request.url,
                "found_students": len(raw_data),
                "valid_students": 0,
                "suggestions": [
                    "The webpage data format may not match our expected schema",
                    "Required fields: student_id, first_name, last_name",
                    "Check data quality in the source webpage"
                ]
            }
        
        # Convert to Student model objects for report generation
        student_objects = []
        for student_data in students_data:
            student_dict = student_data.dict() if hasattr(student_data, 'dict') else student_data
            student_obj = Student(**student_dict)
            student_objects.append(student_obj)
        
        # Generate comprehensive report with Excel and charts
        report_info = report_generator.generate_comprehensive_report(
            students=student_objects,
            report_type="crawl",
            additional_info={
                "source_url": crawl_request.url,
                "parse_type": crawl_request.parse_type,
                "crawl_timestamp": report_info["timestamp"] if 'report_info' in locals() else None
            }
        )
        
        return {
            "success": True,
            "message": "Successfully crawled and generated report",
            "crawl_url": crawl_request.url,
            "parse_type": crawl_request.parse_type,
            "found_students": len(raw_data),
            "valid_students": len(students_data),
            "report": {
                "folder": report_info["report_folder"],
                "excel_file": report_info["excel_file"],
                "total_charts": len(report_info["charts"]),
                "charts": [chart["name"] for chart in report_info["charts"]],
                "summary_file": report_info["summary_file"]
            },
            "preview": [s.dict() if hasattr(s, 'dict') else s for s in students_data[:5]]
        }
        
    except ValueError as e:
        # Handle report generation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Report generation error: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to crawl website: {str(e)}"
        )

@router.post("/crawl-and-import", response_model=Dict[str, Any])
async def crawl_and_import(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crawl student data from a website, import to database, and generate report"""
    
    try:
        crawler = CrawlerService()
        
        # Crawl data
        if crawl_request.parse_type == "auto":
            raw_data = crawler.auto_detect_student_data(crawl_request.url)
        elif crawl_request.parse_type == "student_list":
            raw_data = crawler.crawl_student_list(crawl_request.url)
        elif crawl_request.parse_type == "single_student":
            student_data = crawler.crawl_student_detail(crawl_request.url)
            raw_data = [student_data] if student_data else []
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parse_type"
            )
        
        if not raw_data:
            return {
                "success": False,
                "message": "No student data found on the webpage",
                "crawl_url": crawl_request.url,
                "import_result": None,
                "report": None
            }
        
        # Clean and validate data
        students_data = crawler.clean_crawled_data(raw_data)
        
        if not students_data:
            return {
                "success": False,
                "message": "No valid student data could be extracted",
                "crawl_url": crawl_request.url,
                "import_result": None,
                "report": None
            }
        
        # Import to database
        created_students, errors = student_crud.bulk_create(db=db, students_in=students_data)
        
        # Generate report if students were successfully imported
        report_info = None
        if created_students:
            report_info = report_generator.generate_comprehensive_report(
                students=created_students,
                report_type="crawl_import",
                additional_info={
                    "source_url": crawl_request.url,
                    "parse_type": crawl_request.parse_type,
                    "total_processed": len(students_data),
                    "successful_imports": len(created_students),
                    "failed_imports": len(students_data) - len(created_students)
                }
            )
        
        return {
            "success": True,
            "message": f"Successfully imported {len(created_students)} students",
            "crawl_url": crawl_request.url,
            "import_result": {
                "total_processed": len(students_data),
                "successful_imports": len(created_students),
                "failed_imports": len(students_data) - len(created_students),
                "errors": errors,
                "imported_student_ids": [s.student_id for s in created_students]
            },
            "report": {
                "folder": report_info["report_folder"],
                "excel_file": report_info["excel_file"],
                "total_charts": len(report_info["charts"]),
                "charts": [chart["name"] for chart in report_info["charts"]],
                "summary_file": report_info["summary_file"]
            } if report_info else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to crawl and import: {str(e)}"
        )

@router.post("/test-crawl", response_model=Dict[str, Any])
async def test_crawl(
    url: str,
    parse_type: str = "auto"
):
    """Test crawling a website without saving data"""
    
    try:
        crawler = CrawlerService()
        
        if parse_type == "auto":
            raw_data = crawler.auto_detect_student_data(url)
        elif parse_type == "student_list":
            raw_data = crawler.crawl_student_list(url)
        elif parse_type == "single_student":
            student_data = crawler.crawl_student_detail(url)
            raw_data = [student_data] if student_data else []
        else:
            raw_data = crawler.auto_detect_student_data(url)
        
        return {
            "url": url,
            "parse_type": parse_type,
            "found_records": len(raw_data),
            "raw_data_preview": raw_data[:3] if raw_data else [],
            "success": len(raw_data) > 0
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to test crawl: {str(e)}"
        )

@router.get("/supported-sites")
def get_supported_sites():
    """Get information about supported website formats for crawling"""
    
    return {
        "supported_formats": {
            "table_based": {
                "description": "Websites with HTML tables containing student data",
                "selectors": ["table", "tr", "td", "th"],
                "example": "University student lists in table format"
            },
            "structured_html": {
                "description": "Websites with structured HTML elements",
                "selectors": ["div", "span", "p with data attributes"],
                "example": "Student profile pages with consistent HTML structure"
            }
        },
        "parse_types": {
            "auto": "Automatically detect student data structure",
            "student_list": "Parse table-based student lists",
            "single_student": "Parse individual student detail pages"
        },
        "output_formats": {
            "excel": "Save to Excel file only",
            "json": "Return JSON data only",
            "all": "Save to Excel and return JSON"
        },
        "required_fields": ["student_id", "first_name", "last_name"],
        "optional_fields": ["email", "birth_date", "hometown", "math_score", "literature_score", "english_score"]
    }


@router.post("/generate-report", response_model=Dict[str, Any])
async def generate_report_from_db(
    db: Session = Depends(get_db),
    limit: int = 1000
):
    """Generate comprehensive report from existing students in database"""
    
    try:
        # Fetch students from database (returns tuple of (students, total_count))
        students, total_count = student_crud.get_multi(db=db, skip=0, limit=limit)
        
        if not students:
            return {
                "success": False,
                "message": "No students found in database",
                "total_students": 0,
                "report": None
            }
        
        # Generate comprehensive report
        report_info = report_generator.generate_comprehensive_report(
            students=students,
            report_type="database_export",
            additional_info={
                "source": "database",
                "total_students": len(students),
                "total_in_db": total_count
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully generated report for {len(students)} students",
            "total_students": len(students),
            "total_in_database": total_count,
            "report": {
                "folder": report_info["report_folder"],
                "excel_file": report_info["excel_file"],
                "total_charts": len(report_info["charts"]),
                "charts": [chart["name"] for chart in report_info["charts"]],
                "summary_file": report_info["summary_file"],
                "timestamp": report_info["timestamp"]
            }
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Report generation error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report: {str(e)}"
        )