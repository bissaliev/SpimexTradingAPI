import io
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd

from exceptions import XLSExtractorError
from app.configs.logging_config import logger


class XLSExtractor:
    """Класс работает с файлами *.xls.Позволяет извлекать данные из файла"""

    sheet_name: str = "TRADE_SUMMARY"
    table_name = "Единица измерения: Метрическая тонна"

    def __init__(self, file: io.BytesIO, bidding_date: date):
        try:
            if file.getbuffer().nbytes == 0:
                raise ValueError("Файл пустой, загрузка невозможна!")
            else:
                self.bidding_date = bidding_date
                self.dataframe: pd.DataFrame = self._load_xls(file)
                logger.info(f"Файл преобразован в DataFrame для даты {bidding_date}")
        except ValueError as e:
            raise XLSExtractorError(e) from e

    def _load_xls(self, file) -> pd.DataFrame:
        """Загружает данные из xls-файла в DataFrame."""
        return pd.read_excel(file, sheet_name=self.sheet_name, header=None)

    def _find_start_index(self) -> int:
        """Находит индекс строки, содержащей ключевую фразу."""
        match = self.dataframe.stack().astype(str).str.contains(self.table_name)
        indices = match[match].index.get_level_values(0).unique()

        if indices.empty:
            raise ValueError(f"Секция '{self.table_name}' не найдена!")
        return indices[0]

    def _extract_table(self):
        """Обрезает DataFrame с нужного индекса и переименовывает колонки."""
        start_idx = self._find_start_index()
        self.df = self.dataframe.iloc[start_idx + 1 :].reset_index(drop=True)
        self.df.columns = self.df.iloc[0].astype(str).str.replace("\n", " ").str.strip()
        return self.df.iloc[1:].reset_index(drop=True)  # Убираем заголовок

    def _filter_valid_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Фильтрует строки, оставляя только те, где количество договоров > 0.
        """
        count_col = next(col for col in df.columns if "Количество Договоров" in col)
        df = df[df[count_col].astype(str).str.isnumeric()]
        df = df[df[count_col].astype(int) > 0]
        return df.iloc[:-2]  # Удаляем последние 2 строки с итогами

    def _to_dict(self, df: pd.DataFrame) -> list[dict[str, Any]]:
        """Преобразует отфильтрованные данные в список словарей."""
        current_datetime = datetime.now()
        records = []
        for _, row in df.iterrows():
            records.append(
                {
                    "exchange_product_id": row["Код Инструмента"],
                    "exchange_product_name": row["Наименование Инструмента"],
                    "oil_id": row["Код Инструмента"][:4],
                    "delivery_basis_id": row["Код Инструмента"][4:7],
                    "delivery_basis_name": row["Базис поставки"],
                    "delivery_type_id": row["Код Инструмента"][-1],
                    "volume": int(row["Объем Договоров в единицах измерения"]),
                    "total": Decimal(row["Обьем Договоров, руб."]),
                    "count": int(row["Количество Договоров, шт."]),
                    "date": self.bidding_date,
                    "created_on": current_datetime,
                    "updated_on": current_datetime,
                }
            )
        return records

    def get_data(self) -> list[dict[str, Any]]:
        """Возвращает данные в виде списка словарей"""
        try:
            data = self._to_dict(self._filter_valid_rows(self._extract_table()))
            return data
        except (ValueError, KeyError, StopIteration) as e:
            raise XLSExtractorError(f"Ошибка при обработке XLS-файла: {e}") from e
        except Exception as e:
            raise XLSExtractorError(f"Неизвестная ошибка при обработке файла: {e}") from e
