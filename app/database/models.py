import datetime as dt
from decimal import Decimal

from sqlalchemy import Date, func, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from database.database import BaseModel


class SpimexTradingResults(BaseModel):
    __tablename__ = "spimex_trading_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exchange_product_id: Mapped[str] = mapped_column(String(20))
    exchange_product_name: Mapped[str] = mapped_column(String(250))
    oil_id: Mapped[str] = mapped_column(String(4), index=True)
    delivery_basis_id: Mapped[str] = mapped_column(String(4), index=True)
    delivery_basis_name: Mapped[str] = mapped_column(String(250))
    delivery_type_id: Mapped[str] = mapped_column(String(4), index=True)
    volume: Mapped[int]
    total: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    count: Mapped[int]
    date: Mapped[dt.date] = mapped_column(Date, index=True)
    created_on: Mapped[dt.datetime] = mapped_column(server_default=func.now(), default=dt.datetime.now)
    updated_on: Mapped[dt.datetime] = mapped_column(server_default=func.now(), onupdate=dt.datetime.now)
