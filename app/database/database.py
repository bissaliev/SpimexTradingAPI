from functools import wraps
from typing import Any, Callable

from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.configs.config import settings

DATABASE_URL = settings.get_db_postgres_url()
# DATABASE_URL = settings.get_db_sqlite_url()

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_timeout=60, pool_pre_ping=True)


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


def async_context_session(func: Callable[..., Any]) -> Callable[..., Any]:
    """Декоратор для управления сессией SQLAlchemy"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        async with AsyncSessionLocal() as session:
            try:
                result = await func(session, *args, **kwargs)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                raise e

    return wrapper
