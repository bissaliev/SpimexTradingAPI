from collections.abc import AsyncGenerator, Generator
from datetime import date
from typing import Any
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from httpx import ASGITransport, AsyncClient
from services.tradings import TradingService
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from api.dependencies import trading_service
from api.routers.tradings import router
from configs.config import settings
from database.database import BaseModel
from database.models import SpimexTradingResults


@pytest_asyncio.fixture
async def test_redis_cache() -> AsyncGenerator[aioredis.Redis, None]:
    """Инициализирует fastapi_cache перед тестами"""
    redis = await aioredis.from_url(f"redis://{settings.TEST_REDIS_HOST}:{settings.TEST_REDIS_PORT}", encoding="utf8")
    FastAPICache.init(RedisBackend(redis), prefix="test-cache")
    yield redis
    await redis.flushdb()


@pytest_asyncio.fixture
async def test_database_engine() -> AsyncGenerator:
    """Заполняет тестовую базу данных начальными данными перед тестами."""
    database_url = (
        f"postgresql+asyncpg://{settings.TEST_POSTGRES_USER}:{settings.TEST_POSTGRES_PASSWORD}"
        f"@{settings.TEST_DB_HOST}:{settings.TEST_DB_PORT}/{settings.TEST_POSTGRES_DB}"
    )
    test_engine = create_async_engine(database_url, future=True, echo=True)
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    yield test_engine
    async with test_engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.drop_all)


@pytest_asyncio.fixture
async def populate_test_database(session: AsyncSession, trading_data: list[dict[str, Any]]) -> None:
    """Создает и удаляет тестовую базу данных перед и после тестов."""

    await session.execute(insert(SpimexTradingResults), trading_data)
    await session.commit()


@pytest_asyncio.fixture
async def session(test_database_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = sessionmaker(bind=test_database_engine, class_=AsyncSession)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture
async def mock_session() -> AsyncMock:
    """Создает мок-сессию для тестирования зависимостей, использующих БД."""
    return AsyncMock(spec=AsyncSession)


def start_application() -> FastAPI:
    """Создает экземпляр FastAPI с подключенным маршрутом торгов."""
    test_app = FastAPI()
    test_app.include_router(router, prefix="/trading")
    return test_app


@pytest.fixture
def test_app() -> Generator[FastAPI, None, None]:
    """Фикстура, создающая тестовый экземпляр FastAPI."""
    _app = start_application()
    yield _app


@pytest.fixture
def client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Фикстура, создающая синхронный тестовый клиент."""
    with TestClient(test_app) as client:
        yield client


@pytest_asyncio.fixture
async def async_client(test_app: FastAPI, session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура, создающая асинхронный тестовый клиент"""
    test_app.dependency_overrides[trading_service] = lambda: TradingService(session)
    async with AsyncClient(transport=ASGITransport(test_app), base_url="http://test") as c:
        yield c


@pytest.fixture
def mock_trading_service(test_app: FastAPI) -> Generator[AsyncMock, None, None]:
    """Фикстура для подмены сервиса торгов мок-объектом."""
    mock_service = AsyncMock(spec=TradingService)
    test_app.dependency_overrides[trading_service] = lambda: mock_service
    yield mock_service
    test_app.dependency_overrides.clear()


@pytest.fixture
def trading_data() -> list[dict[str, Any]]:
    """Тестовые данные о торгах без уникального идентификатора."""
    return [
        {
            "exchange_product_id": "A100NVY060F",
            "exchange_product_name": "Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
            "oil_id": "A100",
            "delivery_basis_id": "NVY",
            "delivery_basis_name": "ст. Новоярославская",
            "delivery_type_id": "F",
            "volume": 60,
            "total": 5997120.00,
            "count": 1,
            "date": date(2024, 8, 7),
        },
        {
            "exchange_product_id": "A592ACH005A",
            "exchange_product_name": "Бензин (АИ-100-К5), ст. Стенькино II (ст. отправления)",
            "oil_id": "A592",
            "delivery_basis_id": "ACH",
            "delivery_basis_name": "Ачинский НПЗ",
            "delivery_type_id": "A",
            "volume": 100,
            "total": 6042000.00,
            "count": 1,
            "date": date(2024, 8, 8),
        },
        {
            "exchange_product_id": "A10KZLY060W",
            "exchange_product_name": "Бензин (АИ-100-К5)-Евро, ст. Злынка-Экспорт (промежуточная станция)",
            "oil_id": "A10K",
            "delivery_basis_id": "ZLY",
            "delivery_basis_name": "ст. Злынка-Экспорт",
            "delivery_type_id": "W",
            "volume": 120,
            "total": 10656000.00,
            "count": 2,
            "date": date(2024, 8, 9),
        },
    ]


@pytest.fixture
def trading_data_with_id(trading_data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Тестовые данные о торгах с уникальным идентификатором (для ответов сервиса)."""
    return [{"id": i, **trade} for i, trade in enumerate(trading_data, 1)]
