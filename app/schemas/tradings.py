from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class TradingLastDays(BaseModel):
    dates: list[date]


class Trading(BaseModel):
    id: int
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: int
    total: Decimal
    count: int
    date: date
