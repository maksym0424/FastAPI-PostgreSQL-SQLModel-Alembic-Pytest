import pytest
from unittest.mock import MagicMock
from httpx import ASGITransport, AsyncClient
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from master_server.server import app
from master_server.database.user.model import User
from master_server.dependencies.auth import get_current_user
from .app_test_router import app_test_router


# Fixture to create an in-memory SQLite database and yield the session
@pytest.fixture(name="session")
async def session_fixture():
    # Create an in-memory SQLite database.
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)

    # Create the table in the database.
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="module")
async def test_client():
    app.include_router(app_test_router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as test_async_client:
        yield test_async_client


async def mock_get_current_user():
    return User(id=1, email="example@test.com")


@pytest.fixture(scope="module")
def override_dependencies():
    app.dependency_overrides[get_current_user] = mock_get_current_user
    yield
    app.dependency_overrides.clear()
