from datetime import datetime, timedelta

import redis.asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from configs.config import settings


async def get_redis() -> aioredis.Redis:
    """
    Создает подключение к Redis.

    :return: Экземпляр асинхронного клиента Redis.
    """
    host = settings.REDIS_HOST
    port = settings.REDIS_PORT
    redis = aioredis.from_url(f"redis://{host}:{port}", encoding="utf8", decode_responses=True)
    return redis


async def init_redis() -> aioredis.Redis:
    """
    Инициализирует кэш FastAPI с использованием Redis.

    :return: Экземпляр асинхронного клиента Redis.
    """
    redis_client = await get_redis()
    FastAPICache.init(RedisBackend(redis_client), prefix=settings.CACHE_PREFIX)
    return redis_client


def get_expiries() -> int:
    """
    Рассчитывает время (в секундах) до ближайшего сброса кэша в 14:11.

    :return: Количество секунд до следующего сброса.
    """
    now = datetime.now()
    reset_time = now.replace(hour=14, minute=11, second=0, microsecond=0)
    if now > reset_time:
        reset_time += timedelta(days=1)

    return (reset_time - now).seconds
