"""
Student Management API Endpoints

This module provides REST API endpoints for managing student records including:
- CRUD operations (Create, Read, Update, Delete)
- Advanced analytics using Pandas
- Data filtering and pagination
- Sample data generation

All endpoints return XML format responses.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import Response
from sqlmodel import Session

# Core dependencies and utilities
from app.core.dependencies import get_db
from app.core.exceptions import StudentNotFoundError, StudentAlreadyExistsError
from app.core.pagination import PaginationParams

# CRUD operations and models
from app.crud.student import student_crud
from app.models.student import Student, StudentCreate, StudentUpdate, StudentBase

# Services for business logic
from app.services.data_service import DataService

# XML response builders
from app.utils.xml_response import StudentXMLBuilder, XMLBuilder

# Initialize router for student endpoints
router = APIRouter()

@router.get("")
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
    """
    Get list of students with pagination, filtering, and sorting
    
    Query Parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 10)
        - search: Search term for student_id, name, or email
        - hometown: Filter by hometown
        - min_average: Minimum average score (0-10)
        - max_average: Maximum average score (0-10)
        - sort_by: Field to sort by
        - sort_order: Sort direction (asc/desc)
    
    Returns:
        XML response with paginated student list
    """
    
    # Query database with filters and pagination
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
    
    # Convert student objects to response dictionaries with computed fields
    student_responses = []
    for student in students:
        response_dict = {
            **student.dict(),  # Include all student fields
            "full_name": student.get_full_name(),  # Add computed full name
            "average_score": student.get_average_score(),  # Add computed average
            "grade": student.get_grade()  # Add computed grade
        }
        student_responses.append(response_dict)
    
    # Calculate pagination metadata
    total_pages = (total + pagination.page_size - 1) // pagination.page_size
    
    pagination_info = {
        "total": total,  # Total number of students
        "page": pagination.page,  # Current page number
        "page_size": pagination.page_size,  # Items per page
        "total_pages": total_pages,  # Total pages available
        "has_next": pagination.page < total_pages,  # Has next page?
        "has_prev": pagination.page > 1  # Has previous page?
    }
    
    # Convert to XML and return
    xml_content = StudentXMLBuilder.students_to_xml(student_responses, pagination_info)
    
    return Response(
        content=xml_content.encode('utf-8'),
        media_type="application/xml; charset=utf-8"
    )

@router.post("", status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new student
    
    Request Body:
        student: StudentCreate object with student information
            - student_id: Unique student identifier (required)
            - first_name: Student's first name
            - last_name: Student's last name
            - full_name: Alternative to first_name/last_name
            - email: Email address (optional)
            - birth_date: Date of birth (optional)
            - hometown: Student's hometown (optional)
            - math_score: Math score 0-10 (optional)
            - literature_score: Literature score 0-10 (optional)
            - english_score: English score 0-10 (optional)
    
    Returns:
        XML response with created student data (status 201)
    
    Raises:
        400: Invalid data or student_id already exists
    """
    try:
        # Handle full_name vs first_name/last_name conversion
        first_name = student.first_name
        last_name = student.last_name
        
        # If full_name is provided but not first_name/last_name, split it
        if student.full_name and not (first_name and last_name):
            parts = student.full_name.strip().split()
            if len(parts) >= 2:
                first_name = parts[0]  # First word as first name
                last_name = ' '.join(parts[1:])  # Rest as last name
            elif len(parts) == 1:
                first_name = parts[0]
                last_name = ""
        
        # Validate that we have at least one name
        if not (first_name or last_name):
            raise ValueError('Either full_name or first_name/last_name must be provided')
        
        # Create StudentBase object for database insertion
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
        
        # Insert into database
        db_student = student_crud.create(db=db, obj_in=student_data)
        
        # Prepare response with computed fields
        response_dict = {
            **db_student.dict(),
            "full_name": db_student.get_full_name(),
            "average_score": db_student.get_average_score(),
            "grade": db_student.get_grade()
        }
        
        # Convert student object to XML format
        xml_content = StudentXMLBuilder.student_to_xml(response_dict)
        
        # Return XML response with 201 Created status
        return Response(
            content=xml_content,
            media_type="application/xml",
            status_code=status.HTTP_201_CREATED
        )
    except ValueError as e:
        # Handle validation errors
        if "already exists" in str(e):
            raise StudentAlreadyExistsError(student.student_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/pandas-analytics")
def get_pandas_analytics(db: Session = Depends(get_db)):
    """
    Get comprehensive student analytics using pandas DataFrame operations
    
    This endpoint uses pandas to perform advanced statistical analysis on student data,
    including descriptive statistics, correlations, and grouping operations.
    
    Returns:
        XML response containing:
            - total_students: Count of all students
            - descriptive_stats: Mean, std, min, max, quartiles for all scores
            - score_correlations: Correlation matrix between subjects
            - hometown_stats: Student count and average scores grouped by hometown
            - grade_distribution: Count of students by grade (A, B, C, D, F)
            - top_performers: List of top 10 students by average score
    """
    from sqlmodel import select
    from app.utils.serialization import convert_numpy_types, safe_dataframe_to_dict
    
    # Query all students from database
    statement = select(Student)
    students = db.exec(statement).all()
    
    # Return empty analytics if no students in database
    if not students:
        xml_content = XMLBuilder.dict_to_xml({"message": "No students found"}, "analytics")
        return Response(content=xml_content, media_type="application/xml")
    
    # Convert student objects to pandas DataFrame for analysis
    df = DataService.create_analytics_dataframe(students)
    
    # Calculate advanced statistics using DataFrame operations
    advanced_stats = DataService.get_advanced_statistics(df)
    
    # Build comprehensive analytics response
    response = {
        "total_students": len(students),
        "pandas_version": "2.1.4",
        "analytics": convert_numpy_types(advanced_stats),  # Convert numpy types to native Python types
        "data_quality": {
            # Count students with all three subject scores
            "students_with_complete_scores": int(df['has_all_scores'].sum()) if 'has_all_scores' in df.columns else 0,
            # Count students with missing score data
            "students_with_missing_data": int(df['missing_scores_count'].gt(0).sum()) if 'missing_scores_count' in df.columns else 0,
            # Average number of missing scores per student
            "average_missing_scores": float(df['missing_scores_count'].mean()) if 'missing_scores_count' in df.columns else 0.0
        },
        "performance_insights": {
            # Top 5 students by average score
            "best_performers": safe_dataframe_to_dict(df.nlargest(5, 'average_score')[['student_id', 'full_name', 'average_score']]) if 'average_score' in df.columns else [],
            # Top 3 students with highest score variance (most improved/variable performance)
            "most_improved": safe_dataframe_to_dict(df.nlargest(3, 'score_variance')[['student_id', 'full_name', 'score_variance']]) if 'score_variance' in df.columns else []
        }
    }
    
    # Final numpy type conversion for XML compatibility
    response = convert_numpy_types(response)
    
    # Convert dictionary to XML format and return
    xml_content = XMLBuilder.dict_to_xml(response, "analytics")
    return Response(content=xml_content, media_type="application/xml")

@router.get("/{student_id}")
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a single student by student ID or database ID
    
    Path Parameters:
        student_id: Student identifier (can be student_id like 'TEST001' or numeric database ID)
    
    Returns:
        XML response with student data including computed fields
    
    Raises:
        404: Student not found
    
    Note: 
        This endpoint tries to find student by student_id field first,
        then falls back to database ID if the input is numeric
    """
    # First attempt: Look up by student_id string field (e.g., "TEST001")
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    # Second attempt: If not found and input is numeric, try database ID lookup
    if not db_student and student_id.isdigit():
        db_student = student_crud.get(db=db, id=int(student_id))
    
    # Raise 404 if student not found by either method
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    # Build response dictionary with computed fields
    response_dict = {
        **db_student.dict(),
        "full_name": db_student.get_full_name(),
        "average_score": db_student.get_average_score(),
        "grade": db_student.get_grade()
    }
    
    # Convert to XML and return
    xml_content = StudentXMLBuilder.student_to_xml(response_dict)
    return Response(content=xml_content, media_type="application/xml")

@router.get("/by-student-id/{student_id}")
def get_student_by_student_id(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Get student by student_id field only (strict lookup)
    
    Path Parameters:
        student_id: Student's unique identifier string (e.g., 'TEST001')
    
    Returns:
        XML response with student data
    
    Raises:
        404: Student not found
    
    Note:
        This endpoint only looks up by the student_id field,
        unlike /{student_id} which also tries database ID
    """
    # Look up student by student_id field only
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    # Build response with computed fields
    response_dict = {
        **db_student.dict(),
        "full_name": db_student.get_full_name(),
        "average_score": db_student.get_average_score(),
        "grade": db_student.get_grade()
    }
    
    # Convert to XML and return
    xml_content = StudentXMLBuilder.student_to_xml(response_dict)
    return Response(content=xml_content, media_type="application/xml")

@router.put("/{student_id}")
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update student by student ID or database ID
    
    Path Parameters:
        student_id: Student identifier (student_id or numeric database ID)
    
    Request Body:
        student_update: StudentUpdate object with fields to update
            All fields are optional - only provided fields will be updated
            - first_name, last_name, full_name
            - email, birth_date, hometown
            - math_score, literature_score, english_score
    
    Returns:
        XML response with updated student data
    
    Raises:
        404: Student not found
        400: Invalid update data
    """
    # First attempt: Look up by student_id string field
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    # Second attempt: If not found and input is numeric, try database ID
    if not db_student and student_id.isdigit():
        db_student = student_crud.get(db=db, id=int(student_id))
    
    # Raise 404 if student not found
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    try:
        # Update student with provided fields (partial update)
        updated_student = student_crud.update(db=db, db_obj=db_student, obj_in=student_update)
        
        # Build response with updated data and computed fields
        response_dict = {
            **updated_student.dict(),
            "full_name": updated_student.get_full_name(),
            "average_score": updated_student.get_average_score(),
            "grade": updated_student.get_grade()
        }
        
        # Convert to XML and return
        xml_content = StudentXMLBuilder.student_to_xml(response_dict)
        return Response(content=xml_content, media_type="application/xml")
    except ValueError as e:
        # Handle duplicate student_id error
        if "already exists" in str(e):
            raise StudentAlreadyExistsError(student_update.student_id)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete student by student ID or database ID
    
    Path Parameters:
        student_id: Student identifier (student_id or numeric database ID)
    
    Returns:
        204 No Content on successful deletion
    
    Raises:
        404: Student not found
    
    Note:
        This performs a hard delete - the student record is permanently removed
    """
    # First attempt: Look up by student_id string field
    db_student = student_crud.get_by_student_id(db=db, student_id=student_id)
    
    # Second attempt: If not found and input is numeric, try database ID
    if not db_student and student_id.isdigit():
        db_student = student_crud.get(db=db, id=int(student_id))
    
    # Raise 404 if student not found
    if not db_student:
        raise StudentNotFoundError(student_id=student_id)
    
    # Perform hard delete using database ID
    deleted_student = student_crud.delete(db=db, id=db_student.id)
    
    # Verify deletion was successful
    if not deleted_student:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete student"
        )
    
    # Return 204 No Content (FastAPI handles empty response automatically)

@router.post("/generate-sample")
def generate_sample_students(
    count: int = Query(100, ge=1, le=1000, description="Number of students to generate"),
    db: Session = Depends(get_db)
):
    """
    Generate sample student data for testing
    
    Query Parameters:
        count: Number of students to generate (1-1000, default 100)
    
    Returns:
        XML response with generation summary:
            - total_generated: Number of students created
            - successful_inserts: Number successfully inserted
            - failed_inserts: Number of failures
            - errors: List of error messages
            - student_ids: List of generated student IDs
    
    Raises:
        400: Generation or database error
    
    Note:
        Generated students have random Vietnamese names, hometowns,
        and scores between 0-10 for Math, Literature, and English
    """
    try:
        # Generate random student data using Vietnamese names and towns
        students_data = DataService.generate_sample_data(count=count)
        
        # Bulk insert generated students into database
        created_students, errors = student_crud.bulk_create(db=db, students_in=students_data)
        
        # Build summary response
        result = {
            "total_generated": len(students_data),
            "successful_inserts": len(created_students),
            "failed_inserts": len(students_data) - len(created_students),
            "errors": errors,
            "student_ids": [s.student_id for s in created_students]
        }
        
        # Convert result to XML and return
        xml_content = StudentXMLBuilder.generation_result_to_xml(result)
        return Response(content=xml_content, media_type="application/xml")
        
    except Exception as e:
        # Wrap exceptions in HTTP 400 error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate sample data: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate sample data: {str(e)}"
        )