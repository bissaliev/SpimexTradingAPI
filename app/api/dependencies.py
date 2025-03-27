from typing import Annotated

from fastapi import Depends
from services.tradings import TradingService
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db


def trading_service(session: Annotated[AsyncSession, Depends(get_db)]) -> TradingService:
    """
    Функция для создания экземпляра TradingService.

    :param session: Асинхронная сессия базы данных, полученная через Depends(get_db).
    :return: Экземпляр TradingService, использующий переданную сессию.
    """
    return TradingService(session)


TradingServiceDepends = Annotated[TradingService, Depends(trading_service)]
