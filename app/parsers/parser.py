import re
from datetime import date

from bs4 import BeautifulSoup
from bs4.element import Tag

from app.configs.logging_config import logger


class Parser:
    """Парсер страницы с бюллетенями торгов"""

    def __init__(self, content: str, min_year: int, current_year: int):
        self.soup = BeautifulSoup(content, "html.parser")
        self.min_year = min_year
        self.current_year = current_year

    def extract_file_links(self) -> list[tuple[str, date]]:
        """Извлечение ссылок на файл и дату торгов"""
        file_links = []
        for item in self.soup.select(".accordeon-inner__item"):
            try:
                link = self._get_link_to_file(item)
                if not link:
                    continue
                bidding_date = self._get_bidding_date(item)
                if not bidding_date:
                    continue
                if not self._check_year(bidding_date):
                    logger.info(f"Дата {bidding_date} вне диапазона [{self.min_year}, {self.current_year}].")
                    break  # Прерываем цикл, если условие не выполняется
                file_url = link["href"]
                if file_url:
                    file_links.append((file_url, bidding_date))
            except Exception as e:
                logger.error(f"Ошибка при обработке элемента: {e}", exc_info=True)
        logger.info(f"Найдено {len(file_links)} ссылок")
        return file_links

    def _get_link_to_file(self, tag: Tag) -> str:
        """Получение ссылки на файл"""
        return tag.select_one("a.link.xls")

    def _get_bidding_date(self, tag: Tag) -> date | None:
        """Получение даты торгов"""
        try:
            date_span = tag.select_one(".accordeon-inner__item-inner__title span")
            if not date_span:
                return None
            date_text = date_span.text.strip()
            match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", date_text)
            if match:
                day, month, year = match.groups()
            return date(int(year), int(month), int(day))
        except Exception as e:
            logger.error(f"Ошибка при разборе даты: {e}", exc_info=True)
            return None

    def _check_year(self, bidding_date: date) -> bool:
        """Проверка даты торгов на соответствие заданному периоду"""
        return self.min_year <= bidding_date.year <= self.current_year
