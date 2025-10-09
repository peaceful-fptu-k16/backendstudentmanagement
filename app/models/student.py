"""
Student Data Models and Schemas

This module defines all Pydantic/SQLModel models for student entities:
- StudentBase: Base model with common fields and validation
- Student: Database table model with computed properties
- StudentCreate: Schema for creating new students
- StudentUpdate: Schema for updating existing students
- StudentResponse: Schema for API responses with computed fields
- StudentBulkImportResult: Schema for bulk import results

All models include field validation and type checking.
"""

from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field
from pydantic import validator, root_validator
import re

class StudentBase(SQLModel):
    """
    Base student model with common fields shared across all schemas
    
    This serves as the foundation for all student-related models,
    containing core student information and basic validation.
    
    Fields:
        student_id: Unique student identifier (6-12 alphanumeric chars)
        first_name: Student's first name (required)
        last_name: Student's last name (required)
        email: Email address (optional, validated)
        birth_date: Date of birth (optional)
        hometown: Student's hometown (optional)
        math_score: Math score 0-10 (optional)
        literature_score: Literature score 0-10 (optional)
        english_score: English score 0-10 (optional)
    """
    student_id: str = Field(index=True, description="Student ID")
    first_name: str = Field(description="First name")
    last_name: str = Field(description="Last name")
    email: Optional[str] = Field(default=None, description="Email address")
    birth_date: Optional[date] = Field(default=None, description="Date of birth")
    hometown: Optional[str] = Field(default=None, description="Hometown")
    math_score: Optional[float] = Field(default=None, ge=0, le=10, description="Math score (0-10)")
    literature_score: Optional[float] = Field(default=None, ge=0, le=10, description="Literature score (0-10)")
    english_score: Optional[float] = Field(default=None, ge=0, le=10, description="English score (0-10)")
    
    @validator('student_id')
    def validate_student_id(cls, v):
        """
        Validate student_id format and convert to uppercase
        
        Rules:
        - Must not be empty
        - 6-12 alphanumeric characters only
        - Automatically converted to uppercase
        
        Raises:
            ValueError: If student_id is invalid
        """
        if not v:
            raise ValueError('Student ID is required')
        # Alphanumeric validation with length constraint
        if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
            raise ValueError('Student ID must be 6-12 alphanumeric characters')
        return v.upper()  # Standardize to uppercase
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """
        Validate name fields are not empty and trim whitespace
        
        Raises:
            ValueError: If name is empty or only whitespace
        """
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()  # Remove leading/trailing whitespace
    
    @validator('email')
    def validate_email(cls, v):
        """
        Validate email format using regex pattern
        
        Rules:
        - Optional field (None is valid)
        - Must match standard email format if provided
        - Whitespace is trimmed
        
        Raises:
            ValueError: If email format is invalid
        """
        if v is not None and v.strip():
            # Standard email regex pattern
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v

class Student(StudentBase, table=True):
    """
    Student database table model
    
    Extends StudentBase with database-specific fields and computed properties.
    This model maps directly to the 'students' table in the database.
    
    Additional Fields:
        id: Auto-incrementing primary key
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    
    Computed Properties:
        get_full_name(): Returns concatenated first and last name
        get_average_score(): Calculates average from available scores
        get_grade(): Returns grade classification based on average
    """
    __tablename__ = "students"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # ============================================================================
    # Computed Properties
    # ============================================================================
    
    def get_full_name(self) -> str:
        """
        Get student's full name by combining first and last names
        
        Returns:
            str: Full name in format "FirstName LastName"
        """
        return f"{self.first_name} {self.last_name}"
    
    def get_average_score(self) -> Optional[float]:
        """
        Calculate average score from all available subject scores
        
        Only includes non-null scores in the calculation.
        If no scores are available, returns None.
        
        Returns:
            Optional[float]: Average score (0-10) or None if no scores
        """
        # Filter out None values from scores
        scores = [s for s in [self.math_score, self.literature_score, self.english_score] if s is not None]
        return sum(scores) / len(scores) if scores else None
    
    def get_grade(self) -> Optional[str]:
        """
        Get grade classification based on average score
        
        Grade Scale:
        - Excellent: >= 8.5
        - Good: >= 7.0
        - Average: >= 5.5
        - Below Average: >= 4.0
        - Poor: < 4.0
        
        Returns:
            Optional[str]: Grade classification or None if no scores available
        """
        avg = self.get_average_score()
        if avg is None:
            return None
        if avg >= 8.5:
            return "Excellent"
        elif avg >= 7.0:
            return "Good"
        elif avg >= 5.5:
            return "Average"
        elif avg >= 4.0:
            return "Below Average"
        else:
            return "Poor"

class StudentCreate(SQLModel):
    """
    Schema for creating a new student
    
    Supports two methods of providing names:
    1. Separate first_name and last_name fields
    2. Single full_name field (will be split automatically)
    
    All fields are optional to allow flexible validation in the endpoint,
    but student_id and at least one name field are required.
    
    Fields:
        student_id: Unique identifier (required, validated)
        first_name: First name (optional, used with last_name)
        last_name: Last name (optional, used with first_name)
        full_name: Full name (optional, alternative to first_name + last_name)
        email: Email address (optional, validated)
        birth_date: Date of birth (optional)
        hometown: Hometown (optional)
        math_score: Math score 0-10 (optional)
        literature_score: Literature score 0-10 (optional)
        english_score: English score 0-10 (optional)
    """
    student_id: str = Field(index=True, description="Student ID")
    # Support both naming approaches
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")  
    full_name: Optional[str] = Field(default=None, description="Full name (alternative to first_name + last_name)")
    
    email: Optional[str] = Field(default=None, description="Email address")
    birth_date: Optional[date] = Field(default=None, description="Date of birth")
    hometown: Optional[str] = Field(default=None, description="Hometown")
    math_score: Optional[float] = Field(default=None, ge=0, le=10, description="Math score (0-10)")
    literature_score: Optional[float] = Field(default=None, ge=0, le=10, description="Literature score (0-10)")
    english_score: Optional[float] = Field(default=None, ge=0, le=10, description="English score (0-10)")
    
    @validator('student_id')
    def validate_student_id(cls, v):
        """Validate student_id format (see StudentBase for details)"""
        if not v:
            raise ValueError('Student ID is required')
        if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
            raise ValueError('Student ID must be 6-12 alphanumeric characters')
        return v.upper()
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format (see StudentBase for details)"""
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v

class StudentUpdate(SQLModel):
    """
    Schema for updating an existing student
    
    All fields are optional to support partial updates.
    Only provided fields will be updated in the database.
    
    Fields:
        All fields from StudentBase, but all are Optional[type]
        
    Validation:
        - Same validation rules as StudentBase
        - Only applied to non-None values
        - Empty strings are rejected for names
    """
    student_id: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    birth_date: Optional[date] = None
    hometown: Optional[str] = None
    math_score: Optional[float] = Field(default=None, ge=0, le=10)
    literature_score: Optional[float] = Field(default=None, ge=0, le=10)
    english_score: Optional[float] = Field(default=None, ge=0, le=10)
    
    @validator('student_id')
    def validate_student_id(cls, v):
        """Validate student_id if provided (None is allowed for updates)"""
        if v is not None:
            if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
                raise ValueError('Student ID must be 6-12 alphanumeric characters')
            return v.upper()
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        """Validate names if provided (None is allowed, but empty string is not)"""
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty')
            return v.strip()
        return v
    
    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided"""
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v

class StudentResponse(StudentBase):
    """
    Schema for student API responses
    
    Extends StudentBase with database-specific fields and computed properties
    used in API responses. This is the format returned to API clients.
    
    Additional Fields:
        id: Database primary key
        created_at: Creation timestamp
        updated_at: Last update timestamp
        full_name: Computed full name
        average_score: Computed average score
        grade: Computed grade classification
    """
    id: int
    created_at: datetime
    updated_at: datetime
    full_name: str
    average_score: Optional[float] = None
    grade: Optional[str] = None
    
    class Config:
        """Pydantic configuration to enable ORM mode"""
        from_attributes = True  # Allow creation from ORM models

class StudentBulkImportResult(SQLModel):
    """
    Schema for bulk import operation results
    
    Contains statistics and details about a bulk import operation,
    including success/failure counts and error messages.
    
    Fields:
        total_processed: Total number of records processed
        successful_imports: Number of successfully imported students
        failed_imports: Number of failed imports
        errors: List of error messages (with row numbers)
        imported_student_ids: List of successfully imported student IDs
    """
    total_processed: int
    successful_imports: int
    failed_imports: int
    errors: list[str] = []
    imported_student_ids: list[str] = []
