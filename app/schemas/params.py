from datetime import date

from pydantic import BaseModel


class DynamicParams(BaseModel):
    oil_id: str | None = None
    delivery_type_id: str | None = None
    delivery_basis_id: str | None = None
    start_date: date | None = None
    end_date: date | None = None


class LastParams(BaseModel):
    oil_id: str | None = None
    delivery_type_id: str | None = None
    delivery_basis_id: str | None = None
    limit: int = 10
