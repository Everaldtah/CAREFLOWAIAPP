"""
Database Module for CareFlow AI

Handles database connections, sessions, and utilities.
Supports both synchronous and asynchronous operations.
"""

from contextlib import contextmanager, asynccontextmanager
from typing import AsyncGenerator, Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, QueuePool
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# =============================================================================
# Synchronous Database Engine
# =============================================================================
engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,  # Verify connections before use
    echo=settings.is_development,  # Log SQL in development
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)


# =============================================================================
# Asynchronous Database Engine
# =============================================================================
async_engine = create_async_engine(
    settings.database_url_async,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    pool_recycle=settings.database_pool_recycle,
    pool_pre_ping=True,
    echo=settings.is_development,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# =============================================================================
# Session Management
# =============================================================================
def get_db() -> Generator[Session, None, None]:
    """
    Get a synchronous database session.

    Yields:
        Database session

    Example:
        ```python
        with get_db() as db:
            user = db.query(User).first()
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        Database session

    Example:
        ```python
        with get_db_context() as db:
            user = db.query(User).first()
        ```
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an asynchronous database session.

    Yields:
        Async database session

    Example:
        ```python
        async with get_async_db() as db:
            result = await db.execute(select(User))
        ```
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_async_db_context() -> AsyncGenerator[AsyncSession, None]:
    """
    Async context manager for database sessions.

    Yields:
        Async database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


# =============================================================================
# Database Utilities
# =============================================================================
def init_db() -> None:
    """
    Initialize the database.
    Creates all tables if they don't exist.
    """
    from app.core.base import Base  # Import here to avoid circular imports

    Base.metadata.create_all(bind=engine)


async def init_async_db() -> None:
    """
    Initialize the async database.
    Creates all tables if they don't exist.
    """
    from app.core.base import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


def drop_db() -> None:
    """
    Drop all database tables.
    WARNING: This will delete all data!
    """
    from app.core.base import Base

    Base.metadata.drop_all(bind=engine)


async def drop_async_db() -> None:
    """
    Drop all database tables asynchronously.
    WARNING: This will delete all data!
    """
    from app.core.base import Base

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection is successful
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def check_async_db_connection() -> bool:
    """
    Check if async database connection is working.

    Returns:
        True if connection is successful
    """
    try:
        async with async_engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


def close_db() -> None:
    """Close all database connections."""
    engine.dispose()


async def close_async_db() -> None:
    """Close all async database connections."""
    await async_engine.dispose()
