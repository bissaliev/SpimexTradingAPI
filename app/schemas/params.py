from datetime import date

from pydantic import BaseModel, Field


class LimitOffset(BaseModel):
    """
    Модель для пагинации с параметрами `offset` и `limit`.

    :param offset: Смещение для запроса, по умолчанию 0.
    :param limit: Количество элементов на странице, по умолчанию 10.
    """

    offset: int = 0
    limit: int = 10


class TradingParams(BaseModel):
    """
    Базовая модель фильтрации по торговым параметрам.

    :param oil_id: Идентификатор нефтепродукта (строка длиной 4 символа).
    :param delivery_type_id: Идентификатор типа доставки (строка длиной 1 символ).
    :param delivery_basis_id: Идентификатор базы доставки (строка длиной 3 символа).
    """

    oil_id: str | None = Field(None, min_length=4, max_length=4)
    delivery_type_id: str | None = Field(None, min_length=1, max_length=1)
    delivery_basis_id: str | None = Field(None, min_length=3, max_length=3)


class DynamicParams(TradingParams):
    """
    Расширенная модель фильтрации с дополнительными параметрами дат.

    :param start_date: Начальная дата диапазона.
    :param end_date: Конечная дата диапазона.
    """

    start_date: date | None = None
    end_date: date | None = None


class LastParams(TradingParams, LimitOffset):
    """
    Модель для получения последних записей с фильтрацией по торговым параметрам
    и поддержкой пагинации.
    """

    pass
