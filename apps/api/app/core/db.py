"""
Database session management and engine configuration.

Provides SQLAlchemy 2.0 engine, session factory, and declarative base for ORM models.
Use get_db() as a FastAPI dependency to obtain database sessions with automatic cleanup.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    All SQLAlchemy models should inherit from this class to use the declarative system.
    This provides common functionality and ensures consistent table metadata.
    """

    pass


# Create database engine
# SQLAlchemy 2.0 uses create_engine with the connection URL
engine: Engine = create_engine(
    settings.database_url_str,
    echo=settings.database_echo,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_pre_ping=True,  # Verify connections before using them
    future=True,  # Enable SQLAlchemy 2.0 mode
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn: Any, connection_record: Any) -> None:
    """
    Set SQLite-specific pragmas if using SQLite.

    This event handler is only relevant for SQLite databases.
    For PostgreSQL (our primary database), this is a no-op.
    """
    # Only apply to SQLite connections
    if hasattr(dbapi_conn, "execute"):
        cursor = dbapi_conn.cursor()
        # Check if this is actually SQLite
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
        except Exception:
            # Not SQLite or pragma not supported, ignore
            pass


# Create session factory
# Use sessionmaker to create a factory for database sessions
SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # Prevent lazy loading after commit
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Yields a SQLAlchemy session and ensures it's properly closed after use.
    Use this as a dependency in FastAPI route handlers.

    Example:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()

    Yields:
        Session: Database session that will be automatically closed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables.

    This should only be used in development or testing.
    In production, use Alembic migrations instead.

    WARNING: This does not run migrations. Use Alembic for schema changes.
    """
    Base.metadata.create_all(bind=engine)


def dispose_db() -> None:
    """
    Dispose of the database engine and close all connections.

    Call this during application shutdown to ensure clean resource cleanup.
    """
    engine.dispose()
