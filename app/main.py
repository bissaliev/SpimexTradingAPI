from contextlib import asynccontextmanager

from fastapi import FastAPI

from api.routers.tradings import router as trading_router
from utils.redis_client import init_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Контекстный менеджер для управления жизненным циклом приложения.

    Инициализирует подключение к Redis при запуске приложения
    и закрывает его при завершении работы.

    :param app: Экземпляр FastAPI.
    """

    redis_client = await init_redis()
    yield
    await redis_client.close()


app = FastAPI(title="Spimex Trading API", lifespan=lifespan)


app.include_router(trading_router, prefix="/trading", tags=["Trading"])
