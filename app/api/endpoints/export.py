import io
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, HTTPException, status
from fastapi.responses import StreamingResponse, Response
from sqlmodel import Session

from app.core.dependencies import get_db
from app.crud.student import student_crud
from app.services.export_service import ExportService
from app.schemas import ExportRequest

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
    """Export students data in various formats"""
    
    # Get filtered students (without pagination for export)
    students, _ = student_crud.get_multi(
        db=db,
        skip=0,
        limit=10000,  # Large limit for export
        search=search,
        hometown=hometown,
        min_average=min_average,
        max_average=max_average
    )
    
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students found matching the criteria"
        )
    
    # Generate export based on format
    if format == "csv":
        csv_buffer = ExportService.students_to_csv(students, include_analytics)
        
        return StreamingResponse(
            io.StringIO(csv_buffer.getvalue()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=students.csv"}
        )
    
    elif format == "excel":
        excel_buffer = ExportService.students_to_excel(students, include_analytics)
        
        return StreamingResponse(
            io.BytesIO(excel_buffer.getvalue()),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": "attachment; filename=students.xlsx"}
        )
    
    elif format == "json":
        json_content = ExportService.students_to_json(students, include_analytics)
        
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": "attachment; filename=students.json"}
        )
    
    elif format == "xml":
        xml_content = ExportService.students_to_xml(students, include_analytics)
        
        return Response(
            content=xml_content,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=students.xml"}
        )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported export format"
        )

@router.post("/students")
def export_students_with_config(
    export_request: ExportRequest,
    db: Session = Depends(get_db)
):
    """Export students with custom configuration"""
    
    # Apply filters from the request
    filters = export_request.filters or {}
    
    students, _ = student_crud.get_multi(
        db=db,
        skip=0,
        limit=10000,
        search=filters.get("search"),
        hometown=filters.get("hometown"),
        min_average=filters.get("min_average"),
        max_average=filters.get("max_average")
    )
    
    if not students:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No students found matching the criteria"
        )
    
    format_lower = export_request.format.lower()
    
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported export format: {export_request.format}"
        )

@router.get("/template/{format}")
def download_import_template(
    format: str = Path(..., regex="^(csv|excel)$", description="Template format")
):
    """Download import template file"""
    
    if format == "csv":
        # Create CSV template
        csv_content = """student_id,first_name,last_name,email,birth_date,hometown,math_score,literature_score,english_score
SV202001001,Nguyễn,Văn An,sv001@university.edu.vn,2000-01-15,Hà Nội,8.5,7.0,9.0
SV202001002,Trần,Thị Bình,sv002@university.edu.vn,2000-03-22,TP.HCM,7.5,8.5,8.0"""
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=student_import_template.csv"}
        )
    
    elif format == "excel":
        # Create Excel template with sample data
        import pandas as pd
        
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
        
        df = pd.DataFrame(template_data)
        
        excel_buffer = io.BytesIO()
        with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Students', index=False)
            
            # Add instructions sheet
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