from typing import List, Optional, Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, BackgroundTasks
from sqlmodel import Session

from app.core.dependencies import get_db
from app.core.exceptions import StudentNotFoundError, StudentAlreadyExistsError, BulkImportError
from app.core.pagination import PaginationParams
from app.crud.student import student_crud
from app.models.student import Student, StudentCreate, StudentUpdate, StudentResponse, StudentBulkImportResult, StudentBase
from app.schemas import PaginatedResponse
from app.services.data_service import DataService
from app.services.export_service import ExportService

router = APIRouter()

@router.get("", response_model=PaginatedResponse[StudentResponse])
def get_students(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(None, description="Search by student ID, name, or email"),
    hometown: Optional[str] = Query(None, description="Filter by hometown"),
    min_average: Optional[float] = Query(None, ge=0, le=10, description="Minimum average score"),
    max_average: Optional[float] = Query(None, ge=0, le=10, description="Maximum average score"),
    sort_by: Optional[str] = Query(None, description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: Session = Depends(get_db)
):
    """Get students with pagination and filtering"""
    
    students, total = student_crud.get_multi(
        db=db,
        skip=pagination.offset,
        limit=pagination.page_size,
        search=search,
        hometown=hometown,
        min_average=min_average,
        max_average=max_average,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Convert to response models
    student_responses = []
    for student in students:
        response = StudentResponse(
            **student.dict(),
            full_name=student.get_full_name(),
            average_score=student.get_average_score(),
            grade=student.get_grade()
        )
        student_responses.append(response)
    
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    return PaginatedResponse[StudentResponse](
        items=student_responses,
        total=total,
        page=pagination.page,
        page_size=pagination.page_size,
        total_pages=total_pages,
        has_next=pagination.page < total_pages,
        has_prev=pagination.page > 1
    )

@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """Create a new student"""
    try:
        # Handle full_name vs first_name/last_name
        first_name = student.first_name
        last_name = student.last_name
        
        # If full_name is provided but not first_name/last_name, split it
        if student.full_name and not (first_name and last_name):
            parts = student.full_name.strip().split()
            if len(parts) >= 2:
                first_name = parts[0]
                last_name = ' '.join(parts[1:])
            elif len(parts) == 1:
                first_name = parts[0]
                last_name = ""
        
        # Validate that we have names
        if not (first_name or last_name):
            raise ValueError('Either full_name or first_name/last_name must be provided')
        
        # Create StudentBase for database
        student_data = StudentBase(
            student_id=student.student_id,
            first_name=first_name or "",
            last_name=last_name or "",
            email=student.email,
            birth_date=student.birth_date,
            hometown=student.hometown,
            math_score=student.math_score,
            literature_score=student.literature_score,
            english_score=student.english_score
        )
        
        db_student = student_crud.create(db=db, obj_in=student_data)
        return StudentResponse(
            **db_student.dict(),
            full_name=db_student.get_full_name(),
            average_score=db_student.get_average_score(),
            grade=db_student.get_grade()
        )
    except ValueError as e:
        if "already exists" in str(e):
            raise StudentAlreadyExistsError(student.student_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/pandas-analytics", response_model=Dict[str, Any])
def get_pandas_analytics(db: Session = Depends(get_db)):
    """Get comprehensive analytics using pandas operations"""
    from sqlmodel import select
    from app.utils.serialization import convert_numpy_types, safe_dataframe_to_dict
    
    # Get all students
    statement = select(Student)
    students = db.exec(statement).all()
    
    if not students:
        return {"message": "No students found"}
    
    # Create analytics DataFrame
    df = DataService.create_analytics_dataframe(students)
    
    # Get advanced statistics
    advanced_stats = DataService.get_advanced_statistics(df)
    
    # Build response with safe numpy conversion
    response = {
        "total_students": len(students),
        "pandas_version": "2.1.4",
        "analytics": convert_numpy_types(advanced_stats),
        "data_quality": {
            "students_with_complete_scores": int(df['has_all_scores'].sum()) if 'has_all_scores' in df.columns else 0,
            "students_with_missing_data": int(df['missing_scores_count'].gt(0).sum()) if 'missing_scores_count' in df.columns else 0,
            "average_missing_scores": float(df['missing_scores_count'].mean()) if 'missing_scores_count' in df.columns else 0.0
        },
        "performance_insights": {
            "best_performers": safe_dataframe_to_dict(df.nlargest(5, 'average_score')[['student_id', 'full_name', 'average_score']]) if 'average_score' in df.columns else [],
            "most_improved": safe_dataframe_to_dict(df.nlargest(3, 'score_variance')[['student_id', 'full_name', 'score_variance']]) if 'score_variance' in df.columns else []
        }
    }
    
    # Final conversion to ensure all numpy types are converted
    return convert_numpy_types(response)

@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Get student by student ID (not database ID)"""
    # First try to get by student_id string (e.g., TEST001)
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    # If not found and student_id is numeric, try by database ID
    if not db_student and student_id.isdigit():
        db_student = student_crud.get(db=db, id=int(student_id))
    
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    return StudentResponse(
        **db_student.dict(),
        full_name=db_student.get_full_name(),
        average_score=db_student.get_average_score(),
        grade=db_student.get_grade()
    )

@router.get("/by-student-id/{student_id}", response_model=StudentResponse)
def get_student_by_student_id(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Get student by student ID"""
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    return StudentResponse(
        **db_student.dict(),
        full_name=db_student.get_full_name(),
        average_score=db_student.get_average_score(),
        grade=db_student.get_grade()
    )

@router.put("/{student_id}", response_model=StudentResponse)
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """Update student by student ID or database ID"""
    # First try to get by student_id string (e.g., TEST001)
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    # If not found and student_id is numeric, try by database ID
    if not db_student and student_id.isdigit():
        db_student = student_crud.get(db=db, id=int(student_id))
    
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    try:
        updated_student = student_crud.update(db=db, db_obj=db_student, obj_in=student_update)
        return StudentResponse(
            **updated_student.dict(),
            full_name=updated_student.get_full_name(),
            average_score=updated_student.get_average_score(),
            grade=updated_student.get_grade()
        )
    except ValueError as e:
        if "already exists" in str(e):
            raise StudentAlreadyExistsError(student_update.student_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """Delete student by student ID or database ID"""
    # First try to get by student_id string (e.g., TEST001)
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    # If not found and student_id is numeric, try by database ID
    if not db_student and student_id.isdigit():
        db_student = student_crud.get(db=db, id=int(student_id))
    
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    # Delete by database ID
    deleted_student = student_crud.delete(db=db, id=db_student.id)
    
    if not deleted_student:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student"
        )
    
    # For HTTP 204, we should not return anything
    # FastAPI will handle this automatically

@router.post("/bulk-import", response_model=StudentBulkImportResult)
async def bulk_import_students(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Bulk import students from Excel or CSV file"""
    
    # Validate file type
    if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be Excel (.xlsx, .xls) or CSV (.csv) format"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse file based on type
        if file.filename.endswith('.csv'):
            df = DataService.parse_csv_file(content)
        else:
            df = DataService.parse_excel_file(content)
        
        # Clean data
        df_clean = DataService.clean_dataframe(df)
        
        # Convert to StudentCreate objects
        students_data, conversion_errors = DataService.dataframe_to_students(df_clean)
        
        if not students_data:
            raise BulkImportError("No valid student data found in file", conversion_errors)
        
        # Perform bulk create
        created_students, creation_errors = student_crud.bulk_create(db=db, students_in=students_data)
        
        all_errors = conversion_errors + creation_errors
        
        return StudentBulkImportResult(
            total_processed=len(students_data),
            successful_imports=len(created_students),
            failed_imports=len(students_data) - len(created_students),
            errors=all_errors,
            imported_student_ids=[s.student_id for s in created_students]
        )
        
    except Exception as e:
        if isinstance(e, BulkImportError):
            raise e
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process file: {str(e)}"
        )

@router.post("/generate-sample", response_model=StudentBulkImportResult)
def generate_sample_students(
    count: int = Query(100, ge=1, le=1000, description="Number of students to generate"),
    db: Session = Depends(get_db)
):
    """Generate sample student data for testing"""
    try:
        students_data = DataService.generate_sample_data(count=count)
        created_students, errors = student_crud.bulk_create(db=db, students_in=students_data)
        
        return StudentBulkImportResult(
            total_processed=len(students_data),
            successful_imports=len(created_students),
            failed_imports=len(students_data) - len(created_students),
            errors=errors,
            imported_student_ids=[s.student_id for s in created_students]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate sample data: {str(e)}"
        )

@router.get("/{student_id}/xml")
def get_student_xml(
    student_id: int,
    db: Session = Depends(get_db)
):
    """Get student data in XML format"""
    from fastapi.responses import Response
    
    db_student = student_crud.get(db=db, id=student_id)
    if not db_student:
        raise StudentNotFoundError(id=student_id)
    
    xml_content = ExportService.student_to_xml(db_student)
    
    return Response(
        content=xml_content,
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename=student_{student_id}.xml"}
    )