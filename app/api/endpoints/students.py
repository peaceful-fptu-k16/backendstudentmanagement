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

@router.get("/{student_id}")
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
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

@router.put("/{student_id}")
def update_student(
    student_id: str,
    student_update: StudentUpdate,
    db: Session = Depends(get_db)
):
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