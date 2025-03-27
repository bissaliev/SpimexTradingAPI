from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class TradingLastDays(BaseModel):
    """
    Модель для хранения списка последних торговых дней.

    :param dates: Список дат последних торгов.
    """

    dates: list[date]


class Trading(BaseModel):
    """
    Модель торговых данных.

    :param id: Уникальный идентификатор записи.
    :param exchange_product_id: Идентификатор биржевого продукта.
    :param exchange_product_name: Название биржевого продукта.
    :param oil_id: Идентификатор нефтепродукта.
    :param delivery_basis_id: Идентификатор базы доставки.
    :param delivery_basis_name: Название базы доставки.
    :param delivery_type_id: Идентификатор типа доставки.
    :param volume: Объем торгов (в единицах измерения биржи).
    :param total: Общая сумма сделки.
    :param count: Количество сделок.
    :param date: Дата проведения торгов.
    """

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
