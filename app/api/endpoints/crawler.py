from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from sqlmodel import Session

from app.core.dependencies import get_db
from app.schemas import CrawlRequest
from app.services.crawler_service import CrawlerService
from app.services.data_service import DataService
from app.crud.student import student_crud
from app.models.student import StudentBulkImportResult

router = APIRouter()

@router.post("/crawl", response_model=Dict[str, Any])
async def crawl_website(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crawl student data from a website"""
    
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
        
        if not raw_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student data found on the webpage"
            )
        
        # Clean and validate data
        students_data = crawler.clean_crawled_data(raw_data)
        
        if not students_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No valid student data could be extracted"
            )
        
        # Save to Excel if requested
        excel_path = None
        if crawl_request.output_format in ["excel", "all"]:
            excel_filename = f"crawled_students_{crawl_request.url.split('//')[-1].replace('/', '_')}.xlsx"
            excel_path = crawler.save_to_excel([s.dict() for s in students_data], excel_filename)
        
        return {
            "crawl_url": crawl_request.url,
            "found_students": len(raw_data),
            "valid_students": len(students_data),
            "excel_saved": excel_path is not None,
            "excel_path": excel_path,
            "preview": [s.dict() for s in students_data[:5]]  # Show first 5 as preview
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to crawl website: {str(e)}"
        )

@router.post("/crawl-and-import", response_model=StudentBulkImportResult)
async def crawl_and_import(
    crawl_request: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Crawl student data from a website and import to database"""
    
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
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student data found on the webpage"
            )
        
        # Clean and validate data
        students_data = crawler.clean_crawled_data(raw_data)
        
        if not students_data:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No valid student data could be extracted"
            )
        
        # Import to database
        created_students, errors = student_crud.bulk_create(db=db, students_in=students_data)
        
        # Save to Excel in background if requested
        if crawl_request.output_format in ["excel", "all"]:
            excel_filename = f"crawled_students_{crawl_request.url.split('//')[-1].replace('/', '_')}.xlsx"
            background_tasks.add_task(
                crawler.save_to_excel, 
                [s.dict() for s in students_data], 
                excel_filename
            )
        
        return StudentBulkImportResult(
            total_processed=len(students_data),
            successful_imports=len(created_students),
            failed_imports=len(students_data) - len(created_students),
            errors=errors,
            imported_student_ids=[s.student_id for s in created_students]
        )
        
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