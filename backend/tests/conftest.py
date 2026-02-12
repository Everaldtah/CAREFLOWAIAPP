"""
Test configuration and fixtures for CareFlow AI
"""

import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.core.base import Base
from app.core.config import settings


# PostgreSQL test container
@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Create PostgreSQL test container."""
    with PostgresContainer("pgvector/pgvector:pg15") as postgres:
        yield postgres


# Redis test container
@pytest.fixture(scope="session")
def redis_container() -> Generator[RedisContainer, None, None]:
    """Create Redis test container."""
    with RedisContainer("redis:7-alpine") as redis:
        yield redis


# Test database engine
@pytest.fixture(scope="session")
def test_engine(postgres_container: PostgresContainer):
    """Create test database engine."""
    connection_url = postgres_container.get_connection_url()
    engine = create_async_engine(
        connection_url.replace("postgresql://", "postgresql+asyncpg://"),
        echo=False,
    )

    # Create tables
    asyncio.run(Base.metadata.create_all(engine))

    yield engine

    # Drop tables after tests
    asyncio.run(Base.metadata.drop_all(engine))


# Test database session
@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session_maker() as session:
        yield session

    # Cleanup after each test
    await session.rollback()


# Test client fixture
@pytest_asyncio.fixture
async def test_client(db_session: AsyncSession):
    """Create test FastAPI client."""
    from fastapi.testclient import TestClient
    from app.main import app

    from app.core.dependencies import get_async_db

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


# Auth headers fixture
@pytest.fixture
def auth_headers(test_client) -> dict:
    """Get authenticated headers for testing."""
    # Create test user and login
    response = test_client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
            "first_name": "Test",
            "last_name": "User",
            "is_provider": True,
        },
    )

    login_response = test_client.post(
        "/api/v1/auth/login",
        json={
            "email": "test@example.com",
            "password": "Test123!@#",
        },
    )

    data = login_response.json()
    token = data.get("access_token")

    return {"Authorization": f"Bearer {token}"}
