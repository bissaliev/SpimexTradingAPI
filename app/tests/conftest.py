from collections.abc import Generator
from typing import Any

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import trading_service
from api.routers.tradings import router
from database.database import BaseModel
from tests.dependencies import fake_service
from tests.test_data import tradings


@pytest_asyncio.fixture
async def test_cache():
    """Инициализирует fastapi_cache перед тестами"""
    host = "localhost"
    port = 6378
    redis = await aioredis.from_url(f"redis://{host}:{port}", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="test-cache")
    yield redis
    await redis.flushdb()


@pytest_asyncio.fixture
async def async_db_engine():
    """Создает тестовую БД и применяет миграции"""
    TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5433/test_db"
    test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture
async def session(async_db_engine):
    async_session = sessionmaker(bind=async_db_engine, class_=AsyncSession)
    async with async_session() as session:
        yield session


def start_application():
    app = FastAPI()
    app.include_router(router, prefix="/trading")
    return app


@pytest.fixture(scope="function")
def app() -> Generator[FastAPI, Any, None]:
    _app = start_application()
    yield _app


@pytest.fixture(scope="function")
def client(app: FastAPI):
    app.dependency_overrides[trading_service] = fake_service
    with TestClient(app) as client:
        yield client
        app.dependency_overrides.clear()


@pytest.fixture
def fixtures():
    return tradings
