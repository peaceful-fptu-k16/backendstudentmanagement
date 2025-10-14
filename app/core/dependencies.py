from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from typing import Optional, Generator

def get_session() -> Generator[Session, None, None]:
    from app.database import engine
    with Session(engine) as session:
        yield session

def get_db(session: Session = Depends(get_session)) -> Session:
    return session

async def get_current_user():
    return {"id": 1, "username": "admin", "role": "admin"}

def require_admin(current_user: dict = Depends(get_current_user)):
    if not current_user or current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
