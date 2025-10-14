from typing import Optional
from datetime import datetime, date
from sqlmodel import SQLModel, Field
from pydantic import validator
import re

class StudentBase(SQLModel):
    student_id: str = Field(index=True)
    first_name: str = Field()
    last_name: str = Field()
    email: Optional[str] = Field(default=None)
    birth_date: Optional[date] = Field(default=None)
    hometown: Optional[str] = Field(default=None)
    math_score: Optional[float] = Field(default=None, ge=0, le=10)
    literature_score: Optional[float] = Field(default=None, ge=0, le=10)
    english_score: Optional[float] = Field(default=None, ge=0, le=10)
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v:
            raise ValueError('Student ID is required')
        if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
            raise ValueError('Student ID must be 6-12 alphanumeric characters')
        return v.upper()
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v

class Student(StudentBase, table=True):
    __tablename__ = "students"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    def get_full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    def get_average_score(self) -> Optional[float]:
        if self.math_score is None or self.literature_score is None or self.english_score is None:
            return None
        return (self.math_score + self.literature_score + self.english_score) / 3
    
    def get_grade(self) -> Optional[str]:
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
    student_id: str = Field(index=True)
    first_name: Optional[str] = Field(default=None)
    last_name: Optional[str] = Field(default=None)
    full_name: Optional[str] = Field(default=None)
    
    email: Optional[str] = Field(default=None)
    birth_date: Optional[date] = Field(default=None)
    hometown: Optional[str] = Field(default=None)
    math_score: Optional[float] = Field(default=None, ge=0, le=10)
    literature_score: Optional[float] = Field(default=None, ge=0, le=10)
    english_score: Optional[float] = Field(default=None, ge=0, le=10)
    
    @validator('student_id')
    def validate_student_id(cls, v):
        if not v:
            raise ValueError('Student ID is required')
        if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
            raise ValueError('Student ID must be 6-12 alphanumeric characters')
        return v.upper()
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v

class StudentUpdate(SQLModel):
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
        if v is not None:
            if not re.match(r'^[A-Za-z0-9]{6,12}$', v):
                raise ValueError('Student ID must be 6-12 alphanumeric characters')
            return v.upper()
        return v
    
    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError('Name cannot be empty')
            return v.strip()
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if v is not None and v.strip():
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, v.strip()):
                raise ValueError('Invalid email format')
            return v.strip()
        return v

class StudentResponse(StudentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    full_name: str
    average_score: Optional[float] = None
    grade: Optional[str] = None
    
    class Config:
        from_attributes = True

class StudentBulkImportResult(SQLModel):
    total_processed: int
    successful_imports: int
    failed_imports: int
    errors: list[str] = []
    imported_student_ids: list[str] = []
