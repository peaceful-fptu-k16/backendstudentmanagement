"""
Pagination Utilities

This module provides pagination functionality for database queries.
Includes parameter handling, result containers, and pagination logic.
"""

from typing import Generic, TypeVar, List, Optional
from fastapi import Query
from sqlmodel import Session, select, func
from math import ceil

# Generic type variable for pagination
T = TypeVar('T')

class PaginationParams:
    """
    Pagination parameters for API endpoints
    
    Extracts and validates pagination parameters from query string.
    Automatically calculates offset for database queries.
    
    Attributes:
        page: Current page number (1-based, minimum 1)
        page_size: Number of items per page (1-100)
        offset: Calculated offset for database query (0-based)
    
    Usage:
        @router.get("/students")
        def get_students(pagination: PaginationParams = Depends()):
            # pagination.page, pagination.page_size, pagination.offset
    """
    
    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        """
        Initialize pagination parameters
        
        Args:
            page: Page number (default: 1, min: 1)
            page_size: Items per page (default: 20, min: 1, max: 100)
        """
        self.page = page
        self.page_size = page_size
        # Calculate zero-based offset for database query
        self.offset = (page - 1) * page_size

class PaginatedResult(Generic[T]):
    """
    Container for paginated query results
    
    Generic class that holds paginated data and metadata about the pagination.
    Automatically calculates total pages and navigation flags.
    
    Type Parameters:
        T: Type of items in the result list
    
    Attributes:
        items: List of items for current page
        total: Total number of items across all pages
        page: Current page number
        page_size: Number of items per page
        total_pages: Total number of pages (calculated)
        has_next: Whether there's a next page available
        has_prev: Whether there's a previous page available
    
    Example:
        result: PaginatedResult[Student] = paginate(db, query, 1, 20)
        students = result.items  # List[Student]
        if result.has_next:
            # Show next page button
    """
    
    def __init__(
        self,
        items: List[T],
        total: int,
        page: int,
        page_size: int
    ):
        """
        Initialize paginated result
        
        Args:
            items: List of items for current page
            total: Total count of items
            page: Current page number
            page_size: Items per page
        """
        self.items = items
        self.total = total
        self.page = page
        self.page_size = page_size
        
        # Calculate total pages (rounded up)
        self.total_pages = ceil(total / page_size) if page_size > 0 else 0
        
        # Determine navigation availability
        self.has_next = page < self.total_pages
        self.has_prev = page > 1

def paginate(
    db: Session,
    query,
    page: int,
    page_size: int
) -> PaginatedResult:
    """
    Paginate a SQLModel query
    
    Executes the query with LIMIT and OFFSET, and returns results
    along with pagination metadata.
    
    Args:
        db: Database session
        query: SQLModel select query (before limit/offset applied)
        page: Page number (1-based, must be >= 1)
        page_size: Number of items per page
    
    Returns:
        PaginatedResult: Container with paginated items and metadata
    
    Example:
        from sqlmodel import select
        from app.models import Student
        
        query = select(Student).where(Student.hometown == "Hanoi")
        result = paginate(db, query, page=1, page_size=20)
        
        for student in result.items:
            print(student.full_name)
        print(f"Page {result.page} of {result.total_pages}")
    """
    # Get total count using subquery
    # This counts all rows that match the query before pagination
    count_query = select(func.count()).select_from(query.subquery())
    total = db.exec(count_query).one()
    
    # Calculate offset for current page (zero-based)
    offset = (page - 1) * page_size
    
    # Apply pagination to query
    paginated_query = query.offset(offset).limit(page_size)
    
    # Execute paginated query
    items = db.exec(paginated_query).all()
    
    # Return results wrapped in PaginatedResult container
    return PaginatedResult(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )
