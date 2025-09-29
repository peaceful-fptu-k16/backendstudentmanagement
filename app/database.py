from sqlmodel import SQLModel, create_engine
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # Set to True for SQL logging
    connect_args={"check_same_thread": False}  # For SQLite
)

def create_db_and_tables():
    """Create database tables"""
    SQLModel.metadata.create_all(engine)