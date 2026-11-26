"""
Database connection (SQLAlchemy).
Every request gets its own session, which is closed when the request ends.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import DATABASE_URL

# check_same_thread=False: SQLite normally allows one thread; FastAPI uses several
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """Parent class for all database tables."""


def get_db():
    """FastAPI dependency: open a session for one request, always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
