from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.database import get_db
from database.models import SpimexTradingResults
from schemas.params import DynamicParams, LastParams
from schemas.tradings import Trading, TradingLastDays

router = APIRouter()


@router.get("/last_trading_dates")
async def get_last_trading_dates(db: Annotated[AsyncSession, Depends(get_db)], limit: int = 10) -> TradingLastDays:
    results = await db.execute(
        select(SpimexTradingResults.date).distinct().order_by(SpimexTradingResults.date.desc()).limit(limit)
    )
    return TradingLastDays(dates=results.scalars().all())


@router.get("/dynamics")
async def get_dynamics(
    db: Annotated[AsyncSession, Depends(get_db)], params: Annotated[DynamicParams, Depends()]
) -> list[Trading]:
    stmt = select(SpimexTradingResults)

    if params.oil_id:
        stmt = stmt.where(SpimexTradingResults.oil_id == params.oil_id)

    if params.delivery_type_id:
        stmt = stmt.where(SpimexTradingResults.delivery_type_id == params.delivery_type_id)

    if params.delivery_basis_id:
        stmt = stmt.where(SpimexTradingResults.delivery_basis_id == params.delivery_basis_id)

    if params.start_date:
        stmt = stmt.where(SpimexTradingResults.date >= params.start_date)

    if params.end_date:
        stmt = stmt.where(SpimexTradingResults.date <= params.end_date)

    results = await db.scalars(stmt)
    return results.all()


@router.get("/trading_results")
async def get_trading_results(
    db: Annotated[AsyncSession, Depends(get_db)], params: Annotated[LastParams, Depends()]
) -> list[Trading]:
    stmt = select(SpimexTradingResults)
    if params.delivery_basis_id:
        stmt = stmt.where(SpimexTradingResults.delivery_basis_id == params.delivery_basis_id)

    if params.oil_id:
        stmt = stmt.where(SpimexTradingResults.oil_id == params.oil_id)

    if params.delivery_type_id:
        stmt = stmt.where(SpimexTradingResults.delivery_type_id == params.delivery_type_id)

    stmt = stmt.limit(params.limit)
    results = await db.scalars(stmt)
    return results.all()
