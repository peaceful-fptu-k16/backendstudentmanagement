"""
HTML Crawl and Visualization Endpoint

This endpoint crawls student data from frontend HTML,
exports to Excel, and generates visualization charts.
"""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse, JSONResponse
from sqlmodel import Session
from pathlib import Path
import os
from datetime import datetime

from app.core.dependencies import get_db
from app.services.html_crawler_service import HTMLCrawlerService
from app.services.excel_export_service import ExcelExportService
from app.services.chart_service import ChartService

router = APIRouter()

@router.post("/crawl", response_model=Dict[str, Any])
async def crawl_html_and_generate_reports(
    db: Session = Depends(get_db)
):
    """
    Crawl student data from frontend HTML file, create Excel report and charts
    
    This endpoint:
    1. Parses index.html to extract student table structure
    2. Fetches current student data from database
    3. Exports data to Excel file with formatting
    4. Generates statistical charts using matplotlib
    5. Saves files to reports/ directory
    
    Returns:
        JSON response with file paths and statistics
    
    Raises:
        404: If HTML file not found
        500: If crawl or export fails
    """
    
    try:
        # Initialize services
        excel_service = ExcelExportService()
        
        # Get all students from database
        from app.crud.student import student_crud
        students, total = student_crud.get_multi(
            db=db,
            skip=0,
            limit=10000  # Get all students
        )
        
        if not students:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No student data found in database"
            )
        
        # Create reports directory if not exists
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 4: Export to Excel
        excel_filename = f"students_report_{timestamp}.xlsx"
        excel_path = reports_dir / excel_filename
        
        excel_service.create_excel_report(
            students=students,
            output_path=str(excel_path),
            include_charts=True
        )
        
        # Step 5: Generate charts
        charts_dir = reports_dir / "charts"
        charts_dir.mkdir(exist_ok=True)
        
        # Initialize chart service with custom output directory
        chart_service = ChartService(output_dir=str(charts_dir))
        chart_files = chart_service.generate_all_charts(students=students)
        
        # Step 6: Calculate statistics
        from app.crud.student import student_crud as crud
        analytics = crud.get_analytics(db=db)
        
        # Prepare response
        response = {
            "success": True,
            "message": "Crawl và tạo báo cáo thành công",
            "data": {
                "total_students": len(students),
                "excel_file": str(excel_path),
                "chart_files": chart_files,
                "timestamp": timestamp,
                "statistics": {
                    "total_students": analytics.get("total_students", 0),
                    "average_scores": analytics.get("average_scores", {}),
                    "grade_distribution": analytics.get("grade_distribution", {}),
                    "hometown_distribution": analytics.get("hometown_distribution", {})
                }
            }
        }
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during crawl and report generation: {str(e)}"
        )

@router.get("/download-excel/{filename}")
async def download_excel_report(filename: str):
    """
    Download generated Excel report
    
    Args:
        filename: Name of the Excel file to download
    
    Returns:
        FileResponse with Excel file
    """
    file_path = Path("reports") / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@router.get("/download-chart/{filename}")
async def download_chart(filename: str):
    """
    Download generated chart image
    
    Args:
        filename: Name of the chart file to download
    
    Returns:
        FileResponse with PNG image
    """
    file_path = Path("reports") / "charts" / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chart file not found"
        )
    
    return FileResponse(
        path=str(file_path),
        filename=filename,
        media_type="image/png"
    )
