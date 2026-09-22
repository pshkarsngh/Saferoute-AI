"""Database engine, session factory, and declarative base.

Uses SQLAlchemy 2.0 style. Defaults to SQLite for zero-config dev; production
uses PostgreSQL via DATABASE_URL. All schema changes must go through Alembic
migrations (`backend/alembic/`); `create_all` is a convenience for dev/tests.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

settings = get_settings()

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. Dev/test convenience; production uses Alembic."""
    # Import models so they register on Base metadata.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)