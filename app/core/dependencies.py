from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, Generator

def get_session() -> Generator[Session, None, None]:
    """Get database session"""
    from app.database import engine
    with Session(engine) as session:
        yield session

def get_db(session: Session = Depends(get_session)) -> Session:
    """Dependency to get database session"""
    return session

async def get_current_user():
    """Dependency to get current user (placeholder for future authentication)"""
    # This is a placeholder for future authentication implementation
    # For now, we'll return a default user or None
    return {"id": 1, "username": "admin", "role": "admin"}

def require_admin(current_user: dict = Depends(get_current_user)):
    """Dependency to require admin role"""
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user