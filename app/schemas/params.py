from datetime import date

from pydantic import BaseModel, Field


class LimitOffset(BaseModel):
    offset: int = 0
    limit: int = 10


class TradingParams(BaseModel):
    oil_id: str | None = Field(None, min_length=4, max_length=4)
    delivery_type_id: str | None = Field(None, min_length=1, max_length=1)
    delivery_basis_id: str | None = Field(None, min_length=3, max_length=3)


class DynamicParams(TradingParams):
    start_date: date | None = None
    end_date: date | None = None


class LastParams(TradingParams, LimitOffset):
    pass
