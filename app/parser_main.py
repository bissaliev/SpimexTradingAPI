import asyncio
import time
from datetime import date, datetime

from aiohttp import ClientSession, TCPConnector
from sqlalchemy.exc import SQLAlchemyError

from database.crud import mass_create_trade
from exceptions import XLSExtractorError
from app.configs.logging_config import logger
from parsers.parser import Parser
from parsers.scraper import fetch_file, fetch_page
from utils.file_utils import XLSExtractor

BASE_URL = "https://spimex.com"
PAGE_URL = BASE_URL + "/markets/oil_products/trades/results/"
CURRENT_YEAR = datetime.now().year
MIN_YEAR = 2023
FIRST_PAGE = 1
LAST_PAGE = 55
MAX_CONCURRENT_REQUESTS = 15  # Максимальное число одновременных запросов
MAX_DB_CONCURRENT = 10  # Ограничение для операций с базой данных


async def download_data(session: ClientSession, url: str, bidding_date: date, semaphore: asyncio.Semaphore) -> None:
    """Скачивает файл, обрабатывает его и сохраняет данные в БД"""
    try:
        byte_file = await fetch_file(session, url)

        # Создаем класс извлекающий нужные данные из файла xls
        xls_extractor = XLSExtractor(byte_file, bidding_date)
        data = xls_extractor.get_data()
        logger.info(f"Данные готовы к загрузке в БД для даты {bidding_date}")
        # Сохраняем данные в БД
        async with semaphore:
            await mass_create_trade(data)
            logger.info(f"Данные загружены в БД с торгами {bidding_date}")
    except XLSExtractorError as e:
        logger.error(e)
    except SQLAlchemyError as e:
        logger.error(f"Ошибка при сохранении данных б БД: {e}")
    except Exception as e:
        logger.error(f"Неизвестная ошибка: {e}")


async def process_page(session: ClientSession, page: int, semaphore: asyncio.Semaphore):
    """Обрабатывает одну страницу: парсит ссылки и загружает файлы"""
    page_html = await fetch_page(session, PAGE_URL, params={"page": f"page-{page}"})
    if page_html is None:
        logger.error(f"Пропускаем страницу {page}, так как HTML не был загружен")
        return
    logger.info(f"Страница {page} получена.")

    # Создаем класс Parser и извлекаем ссылки на файлы и даты торгов
    parser = Parser(page_html, MIN_YEAR, CURRENT_YEAR)
    file_links: list[tuple[str, date]] = parser.extract_file_links()

    # Создаем задачи для скачивания файлов и сохранения в БД
    tasks = []
    for link, bidding_date in file_links:
        tasks.append(asyncio.create_task(download_data(session, BASE_URL + link, bidding_date, semaphore)))
    await asyncio.gather(*tasks)
    logger.info(f"Страница {page} загружена")


async def main():
    """Главный модуль"""
    tasks = []
    semaphore_db = asyncio.Semaphore(MAX_DB_CONCURRENT)
    connector = TCPConnector(limit=MAX_CONCURRENT_REQUESTS)

    # В цикле проходимся по страницам со ссылка на файлы
    async with ClientSession(connector=connector) as session:
        for page in range(FIRST_PAGE, LAST_PAGE + 1):
            tasks.append(asyncio.create_task(process_page(session, page, semaphore_db)))

        try:
            await asyncio.gather(*tasks)
            logger.info("Загрузка завершена")
        except Exception as e:
            logger.error(f"Неизвестная ошибка: {e}")


if __name__ == "__main__":
    start_time = time.perf_counter()
    asyncio.run(main())
    end_time = time.perf_counter()
    logger.info(f"Время выполнения: {end_time - start_time}")
