from typing import Annotated

from fastapi import APIRouter, Depends

from api.dependencies import TradingServiceDepends
from schemas.params import DynamicParams, LastParams, LimitOffset
from schemas.tradings import Trading, TradingLastDays

router = APIRouter()


@router.get("/last_trading_dates", summary="Список дат последних торговых дней")
async def get_last_trading_dates(
    trading_service: TradingServiceDepends, params: Annotated[LimitOffset, Depends()]
) -> TradingLastDays:
    results = await trading_service.get_last_dates(**params.model_dump())
    return TradingLastDays(dates=results)


@router.get("/dynamics", summary="Список торгов за заданный период")
async def get_dynamics(
    trading_service: TradingServiceDepends, params: Annotated[DynamicParams, Depends()]
) -> list[Trading]:
    results = await trading_service.filter(**params.model_dump(exclude_unset=True))
    return results


@router.get("/trading_results", summary="Список последних торгов")
async def get_trading_results(
    trading_service: TradingServiceDepends, params: Annotated[LastParams, Depends()]
) -> list[Trading]:
    results = await trading_service.filter(**params.model_dump(exclude_unset=True))
    return results
