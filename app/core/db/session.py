"""
Database session management
Database session configuration
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import get_settings

settings = get_settings()

# Construct database URL from environment variables
DATABASE_URL = (
    f"postgresql://{settings.postgres_user}:{settings.postgres_password}"
    f"@{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}"
)

# Create engine with connection pooling (production-ready)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,        # Connection pool size
    max_overflow=20,     # Extra connections when pool is full
    echo=settings.debug  # Log SQL queries in debug mode
)

# Session factory for database connections
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for FastAPI routes to get database session

    Usage:
        @router.get("/projects")
        async def get_projects(db: Session = Depends(get_db)):
            return db.query(Project).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
