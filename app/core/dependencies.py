"""
Dependency Injection Functions

This module provides FastAPI dependency injection functions for:
- Database session management
- User authentication (placeholder for future implementation)
- Authorization and role-based access control
"""

from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, Generator

def get_session() -> Generator[Session, None, None]:
    """
    Create and yield a database session
    
    Yields:
        Session: SQLModel database session
    
    Note:
        Session is automatically closed after request completes.
        Uses context manager to ensure proper cleanup.
    """
    from app.database import engine
    
    # Create session with context manager for automatic cleanup
    with Session(engine) as session:
        yield session

def get_db(session: Session = Depends(get_session)) -> Session:
    """
    Dependency function to inject database session into endpoints
    
    Args:
        session: Database session from get_session dependency
    
    Returns:
        Session: Active database session for the request
    
    Usage:
        @router.get("/students")
        def get_students(db: Session = Depends(get_db)):
            # Use db session here
    """
    return session

async def get_current_user():
    """
    Get current authenticated user (placeholder for future implementation)
    
    Returns:
        dict: User information with id, username, and role
    
    Note:
        This is a placeholder that returns a default admin user.
        In production, this should:
        - Extract and validate JWT token from request headers
        - Query user from database
        - Return actual user object
    """
    # TODO: Implement real authentication with JWT tokens
    # This is a placeholder that always returns an admin user
    return {"id": 1, "username": "admin", "role": "admin"}

def require_admin(current_user: dict = Depends(get_current_user)):
    """
    Dependency to enforce admin-only access to endpoints
    
    Args:
        current_user: Current user from get_current_user dependency
    
    Returns:
        dict: Current user if they have admin role
    
    Raises:
        403 Forbidden: If user doesn't have admin role
    
    Usage:
        @router.delete("/students/{id}")
        def delete_student(id: int, admin: dict = Depends(require_admin)):
            # Only admins can access this endpoint
    """
    # Check if user exists and has admin role
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
