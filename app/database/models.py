from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import func, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from database.database import BaseModel


class SpimexTradingResults(BaseModel):
    __tablename__ = "spimex_trading_results"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    exchange_product_id: Mapped[str] = mapped_column(String(20))
    exchange_product_name: Mapped[str] = mapped_column(String(250))
    oil_id: Mapped[str] = mapped_column(String(4))
    delivery_basis_id: Mapped[str] = mapped_column(String(4))
    delivery_basis_name: Mapped[str] = mapped_column(String(250))
    delivery_type_id: Mapped[str] = mapped_column(String(4))
    volume: Mapped[int]
    total: Mapped[Decimal] = mapped_column(Numeric(20, 2))
    count: Mapped[int]
    date: Mapped[date]
    created_on: Mapped[datetime] = mapped_column(server_default=func.now(), default=datetime.now)
    updated_on: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=datetime.now)
