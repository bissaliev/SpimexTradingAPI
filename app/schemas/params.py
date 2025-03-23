from datetime import date

from pydantic import BaseModel


class TradingParams(BaseModel):
    oil_id: str | None = None
    delivery_type_id: str | None = None
    delivery_basis_id: str | None = None


class DynamicParams(TradingParams):
    start_date: date | None = None
    end_date: date | None = None


class LastParams(TradingParams):
    limit: int = 10
