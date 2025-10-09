"""
Export API Endpoints

This module provides endpoints for exporting student data in various formats.
Supports CSV, Excel, JSON, and XML export with filtering and analytics options.
All exports can include optional analytics data.
"""

import io
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from sqlmodel import Session

from app.core.dependencies import get_db  # Database session dependency
from app.crud.student import student_crud  # Student CRUD operations
from app.services.export_service import ExportService  # Export format converters
from app.schemas import ExportRequest  # Export configuration schema

router = APIRouter()

@router.get("/students")
def export_students(
    format: str = Query("csv", regex="^(csv|excel|json|xml)$", description="Export format"),
    search: Optional[str] = Query(None, description="Search filter"),
    hometown: Optional[str] = Query(None, description="Hometown filter"),
    min_average: Optional[float] = Query(None, ge=0, le=10, description="Minimum average score"),
    max_average: Optional[float] = Query(None, ge=0, le=10, description="Maximum average score"),
    include_analytics: bool = Query(False, description="Include analytics in export"),
    db: Session = Depends(get_db)
):
    """
    Export student data in various file formats (CSV, Excel, JSON, XML)
    
    Query Parameters:
        format: Export format - "csv", "excel", "json", or "xml" (default: "csv")
        search: Search filter for student_id, name, email (optional)
        hometown: Filter by hometown (optional)
        min_average: Minimum average score filter 0-10 (optional)
        max_average: Maximum average score filter 0-10 (optional)
        include_analytics: Include analytics sheet/section in export (default: false)
    
    Returns:
        File download response in requested format:
            - CSV: text/csv with students.csv filename
            - Excel: .xlsx with students.xlsx filename
            - JSON: application/json with students.json filename
            - XML: application/xml with students.xml filename
    
    Raises:
        404: No students found matching criteria
        400: Unsupported export format
    """
    
    # Query students with filters (no pagination for export, use high limit)
    students, _ = student_crud.get_multi(
        db=db,
        skip=0,
        limit=10000,  # Large limit to include all matching students
        search=search,
        hometown=hometown,
        min_average=min_average,
        max_average=max_average
    )
    
    # Abort if no students match the criteria
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students found matching the criteria"
        )
    
    # Generate export file based on requested format
    if format == "csv":
        # Generate CSV with optional analytics
        csv_buffer = ExportService.students_to_csv(students, include_analytics)
        
        return StreamingResponse(
            io.StringIO(csv_buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=students.csv"}
        )
    
    elif format == "excel":
        # Generate Excel workbook with optional analytics sheet
        excel_buffer = ExportService.students_to_excel(students, include_analytics)
        
        return StreamingResponse(
            io.BytesIO(excel_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=students.xlsx"}
        )
    
    elif format == "json":
        # Generate JSON with optional analytics section
        json_content = ExportService.students_to_json(students, include_analytics)
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=students.json"}
        )
    
    elif format == "xml":
        # Generate XML with optional analytics section
        xml_content = ExportService.students_to_xml(students, include_analytics)
        
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=students.xml"}
        )
    
    else:
        # This should never happen due to regex validation, but kept for safety
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format"
        )

@router.post("/students")
def export_students_with_config(
    export_request: ExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export students with custom configuration using POST request body
    
    Request Body:
        export_request: ExportRequest object with:
            - format: Export format (csv, excel, json, xml)
            - filters: Dictionary with search, hometown, min_average, max_average
            - include_analytics: Boolean to include analytics data
            - columns: List of specific columns to export (optional)
    
    Returns:
        File download response in requested format
    
    Raises:
        404: No students found
        400: Unsupported format or invalid configuration
    """
    
    # Extract filters from request body (default to empty dict if not provided)
    filters = export_request.filters or {}
    
    # Query students with filters from request body
    students, _ = student_crud.get_multi(
        db=db,
        skip=0,
        limit=10000,
        search=filters.get("search"),
        hometown=filters.get("hometown"),
        min_average=filters.get("min_average"),
        max_average=filters.get("max_average")
    )
    
    # Abort if no students match
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students found matching the criteria"
        )
    
    # Normalize format to lowercase for comparison
    format_lower = export_request.format.lower()
    
    # Generate export based on format from request body
    if format_lower == "csv":
        csv_buffer = ExportService.students_to_csv(students, export_request.include_analytics)
        
        return StreamingResponse(
            io.StringIO(csv_buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=students.csv"}
        )
    
    elif format_lower == "excel":
        excel_buffer = ExportService.students_to_excel(students, export_request.include_analytics)
        
        return StreamingResponse(
            io.BytesIO(excel_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=students.xlsx"}
        )
    
    elif format_lower == "json":
        json_content = ExportService.students_to_json(students, export_request.include_analytics)
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=students.json"}
        )
    
    elif format_lower == "xml":
        xml_content = ExportService.students_to_xml(students, export_request.include_analytics)
        
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=students.xml"}
        )
    
    else:
        # Return error with the invalid format name
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format: {export_request.format}"
        )

@router.get("/template/{format}")
def download_import_template(
    format: str = Path(..., regex="^(csv|excel)$", description="Template format")
):
    """
    Download import template file for bulk student import
    
    Path Parameters:
        format: Template format - "csv" or "excel"
    
    Returns:
        Template file with sample data and proper column headers:
            - CSV: student_import_template.csv with 2 sample rows
            - Excel: student_import_template.xlsx with formatted headers
    
    Note:
        Template includes all required fields: student_id, first_name, last_name,
        email, birth_date, hometown, math_score, literature_score, english_score
    """
    
    if format == "csv":
        # Create CSV template with headers and sample data
        csv_content = """student_id,first_name,last_name,email,birth_date,hometown,math_score,literature_score,english_score
SV202001001,Nguyễn,Văn An,sv001@university.edu.vn,2000-01-15,Hà Nội,8.5,7.0,9.0
SV202001002,Trần,Thị Bình,sv002@university.edu.vn,2000-03-22,TP.HCM,7.5,8.5,8.0"""
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=student_import_template.csv"}
        )
    
    elif format == "excel":
        # Create Excel template with sample data and instructions sheet
        import pandas as pd
        
        # Define template data with 2 sample rows
        template_data = {
            'student_id': ['SV202001001', 'SV202001002'],
            'first_name': ['Nguyễn', 'Trần'],
            'last_name': ['Văn An', 'Thị Bình'],
            'email': ['sv001@university.edu.vn', 'sv002@university.edu.vn'],
            'birth_date': ['2000-01-15', '2000-03-22'],
            'hometown': ['Hà Nội', 'TP.HCM'],
            'math_score': [8.5, 7.5],
            'literature_score': [7.0, 8.5],
            'english_score': [9.0, 8.0]
        }
        
        # Create DataFrame from template data
        df = pd.DataFrame(template_data)
        
        # Write to Excel buffer with multiple sheets
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            # Main template sheet with sample data
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Instructions sheet with field descriptions
            instructions = pd.DataFrame({
                'Field': [
                    'student_id', 'first_name', 'last_name', 'email', 'birth_date', 
                    'hometown', 'math_score', 'literature_score', 'english_score'
                ],
                'Required': [
                    'Yes', 'Yes', 'Yes', 'No', 'No', 'No', 'No', 'No', 'No'
                ],
                'Format': [
                    'Alphanumeric, 6-12 characters', 'Text', 'Text', 'Valid email',
                    'YYYY-MM-DD', 'Text', '0-10', '0-10', '0-10'
                ],
                'Example': [
                    'SV202001001', 'Nguyễn', 'Văn An', 'sv001@university.edu.vn',
                    '2000-01-15', 'Hà Nội', '8.5', '7.0', '9.0'
                ]
            })
            
            instructions.to_excel(writer, sheet_name='Instructions', index=False)
        
        excel_buffer.seek(0)
        
        return StreamingResponse(
            io.BytesIO(excel_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=student_import_template.xlsx"}
        )