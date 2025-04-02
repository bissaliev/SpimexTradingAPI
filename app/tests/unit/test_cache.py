from datetime import datetime, timedelta
from typing import Any
from unittest.mock import AsyncMock, Mock, patch

import pytest
import redis.asyncio as aioredis
from services.tradings import TradingService

from utils.redis_client import get_expiries


@pytest.mark.parametrize(
    "return_value, expected",
    (
        (datetime(2025, 3, 31, 13, 0, 0), (14 * 3600 + 11 * 60) - (13 * 3600)),
        (datetime(2025, 3, 31, 15, 0, 0), 24 * 3600 - (15 * 3600) + (14 * 3600 + 11 * 60)),
        (datetime(2025, 3, 31, 14, 11, 1), 86399),
    ),
)
@patch("utils.redis_client.datetime")
async def test_get_expiries_return_correct_time(mock_datetime: datetime, return_value: int, expected: int):
    """Тест что функция `get_expiries` возвращает корректное время в секундах для кеша"""
    mock_datetime.now.return_value = return_value
    result = get_expiries()
    assert result == expected


@pytest.mark.usefixtures("test_redis_cache")
class TestCacheUnit:
    """Тестируем работу кеша для TradingService"""

    @pytest.mark.parametrize("method", ("get_last_dates", "filter"))
    async def test_working_redis_cache_trading_service(
        self,
        method: str,
        test_redis_cache: aioredis.Redis,
        mock_session: AsyncMock,
        trading_data: list[dict[str, Any]],
    ):
        """
        Тестируем что кеш сохраняется с корректным временем жизни
        и отдает данные при следующих запросах из кеша до 14.11
        """
        mock_result = Mock()
        mock_result.all.return_value = trading_data
        mock_session.scalars.return_value = mock_result
        trading_service = TradingService(mock_session)
        await getattr(trading_service, method)()

        keys = [key async for key in test_redis_cache.scan_iter("test-cache:*")]
        assert len(keys) == 1

        # Текущее время
        now = datetime.now()
        # Время сброса кеша сегодня в 14:11
        reset_time = now.replace(hour=14, minute=11, second=0, microsecond=0)
        # Если текущее время позже 14:11, используем завтрашний день
        if now > reset_time:
            reset_time = reset_time + timedelta(days=1)

        # Ожидаемое TTL в секундах
        expected_ttl = int((reset_time - now).total_seconds())
        tolerance = 10  # Допустимая погрешность в секундах
        ttl = await test_redis_cache.ttl(keys[0])
        assert ttl > 0, f"Ключ {keys[0]} не имеет времени жизни"
        assert abs(ttl - expected_ttl) <= tolerance, (
            f"TTL ключа {keys[0]} ({ttl}) не соответствует ожидаемому ({expected_ttl})"
        )

        # Проверяем что второй раз данные забираются из кеша
        await getattr(trading_service, method)()
        assert mock_result.all.call_count == 1
        assert mock_session.scalars.call_count == 1
