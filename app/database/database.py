from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncAttrs, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from configs.config import settings

DATABASE_URL = settings.get_db_postgres_url()

engine = create_async_engine(DATABASE_URL, pool_size=20, max_overflow=10, pool_timeout=60, pool_pre_ping=True)


class BaseModel(AsyncAttrs, DeclarativeBase):
    __abstract__ = True


AsyncSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def get_db():
    async with AsyncSessionLocal() as db:
        yield db
