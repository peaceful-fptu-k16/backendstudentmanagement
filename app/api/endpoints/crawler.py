from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session

from app.core.dependencies import get_db
from app.schemas import GenerateReportRequest
from app.services.crawler_service import CrawlerService
from app.services.report_generator_service import report_generator
from app.crud.student import student_crud
from app.models.student import Student

router = APIRouter()

@router.post("/generate-report", response_model=Dict[str, Any])
async def generate_report_from_url(
    request: GenerateReportRequest,
    db: Session = Depends(get_db)
):
    try:
        crawler = CrawlerService()
        
        # Use the current_url from frontend to crawl HTML data
        crawl_url = request.current_url
        
        # Try enhanced crawl_frontend_page method for better HTML parsing
        try:
            raw_data = crawler.crawl_frontend_page(crawl_url)
        except Exception as frontend_error:
            raw_data = []
        
        # If no data found from frontend crawl, try auto-detect as backup
        if not raw_data:
            try:
                raw_data = crawler.auto_detect_student_data(crawl_url)
            except Exception as e:
                pass  # Continue with empty data
        
        # If no data found from crawling HTML, use database as source
        if not raw_data:
            
            # Fetch students from database
            students, total_count = student_crud.get_multi(db=db, skip=0, limit=1000)
            
            if not students:
                return {
                    "success": False,
                    "message": "No student data found from URL and no students in database",
                    "crawl_url": crawl_url,
                    "total_students": 0,
                    "suggestions": [
                        "Add some students to the database first",
                        "Check if the URL contains student data",
                        "Ensure the frontend is properly loaded"
                    ],
                    "report": None
                }
            
            # Generate report from database data
            report_info = report_generator.generate_comprehensive_report(
                students=students,
                report_type="database_export",
                additional_info={
                    "requested_url": crawl_url,
                    "total_students": len(students)
                }
            )
            
            return {
                "success": True,
                "message": f"No data from HTML. Generated report from {len(students)} students in database",
                "crawl_url": crawl_url,
                "data_source": "database",
                "total_students": len(students),
                "report": {
                    "folder": report_info["report_folder"],
                    "excel_file": report_info["excel_file"],
                    "total_charts": len(report_info["charts"]),
                    "charts": [chart["name"] for chart in report_info["charts"]],
                    "summary_file": report_info["summary_file"],
                    "timestamp": report_info["timestamp"]
                }
            }
        
        # Clean and validate crawled data
        students_data = crawler.clean_crawled_data(raw_data)
        
        if not students_data:
            return {
                "success": False,
                "message": "No valid student data could be extracted from URL",
                "crawl_url": crawl_url,
                "found_records": len(raw_data),
                "valid_students": 0,
                "report": None
            }
        
        # Convert to Student model objects for report generation
        student_objects = []
        for student_data in students_data:
            student_dict = student_data.dict() if hasattr(student_data, 'dict') else student_data
            student_obj = Student(**student_dict)
            student_objects.append(student_obj)
        
        # Generate comprehensive report from crawled data
        report_info = report_generator.generate_comprehensive_report(
            students=student_objects,
            report_type="url_crawl",
            additional_info={
                "crawl_url": crawl_url,
                "frontend_base_url": request.frontend_base_url,
                "crawl_timestamp": request.timestamp,
                "total_students": len(student_objects)
            }
        )
        
        return {
            "success": True,
            "message": f"Successfully crawled and generated report for {len(student_objects)} students",
            "crawl_url": crawl_url,
            "data_source": "url_crawl",
            "found_records": len(raw_data),
            "valid_students": len(students_data),
            "total_students": len(student_objects),
            "report": {
                "folder": report_info["report_folder"],
                "excel_file": report_info["excel_file"],
                "total_charts": len(report_info["charts"]),
                "charts": [chart["name"] for chart in report_info["charts"]],
                "summary_file": report_info["summary_file"],
                "timestamp": report_info["timestamp"]
            },
            "preview": [s.dict() if hasattr(s, 'dict') else s for s in student_objects[:5]]
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

