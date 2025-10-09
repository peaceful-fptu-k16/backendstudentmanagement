"""
Custom Exception Classes

This module defines custom exceptions for the Student Management API.
All exceptions inherit from FastAPI's HTTPException and include appropriate
HTTP status codes and error messages.
"""

from fastapi import HTTPException, status

class StudentException(HTTPException):
    """
    Base exception class for all student-related errors
    
    Inherits from FastAPI's HTTPException to automatically convert
    exceptions into proper HTTP error responses.
    
    Args:
        detail: Error message describing what went wrong
        status_code: HTTP status code (default: 400 Bad Request)
    """
    
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

class ValidationException(StudentException):
    """
    Exception raised for data validation errors
    
    Used when request data fails validation (e.g., invalid email format,
    score out of range, missing required fields).
    
    Args:
        detail: Specific validation error message
    
    HTTP Status: 422 Unprocessable Entity
    """
    
    def __init__(self, detail: str):
        super().__init__(detail=detail, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

class StudentNotFoundError(StudentException):
    """
    Exception raised when requested student doesn't exist in database
    
    Can be initialized with either student_id (string identifier) or
    id (database primary key).
    
    Args:
        student_id: Student's unique identifier string (e.g., "TEST001")
        id: Database primary key integer
    
    HTTP Status: 404 Not Found
    
    Examples:
        raise StudentNotFoundError(student_id="TEST001")
        raise StudentNotFoundError(id=123)
    """
    
    def __init__(self, student_id: str = None, id: int = None):
        # Build error message based on which identifier was provided
        if student_id:
            detail = f"Student with ID {student_id} not found"
        elif id:
            detail = f"Student with database ID {id} not found"
        else:
            detail = "Student not found"
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)

class StudentAlreadyExistsError(StudentException):
    """
    Exception raised when attempting to create student with duplicate ID
    
    Thrown when creating a new student with a student_id that already
    exists in the database.
    
    Args:
        student_id: The duplicate student identifier
    
    HTTP Status: 409 Conflict
    """
    
    def __init__(self, student_id: str):
        detail = f"Student with ID {student_id} already exists"
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)

class BulkImportError(StudentException):
    """
    Exception raised during bulk import operations
    
    Used when bulk import fails, optionally includes list of specific
    errors encountered during the import process.
    
    Args:
        detail: General error message
        errors: List of specific error messages for individual records
    
    Attributes:
        errors: List of error details for debugging
    
    HTTP Status: 400 Bad Request
    """
    
    def __init__(self, detail: str, errors: list = None):
        self.errors = errors or []  # Store errors for detailed reporting
        super().__init__(detail=detail)
