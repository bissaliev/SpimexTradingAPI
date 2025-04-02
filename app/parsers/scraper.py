import io

import aiohttp

from configs.logging_config import logger


async def fetch_page(session: aiohttp.ClientSession, url: str, params=None) -> str | None:
    """Запрашиваем страницу и отдаем html-страницу"""
    try:
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            logger.info(f"Страница {response.url} загружена")
            return await response.text()
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка при получении страницы {params['page']}: {e.status}")
        return None


async def fetch_file(session: aiohttp.ClientSession, url: str) -> io.BytesIO | None:
    """Скачиваем файл и отдаем контент байтов"""
    try:
        async with session.get(url, raise_for_status=True) as response:
            response.raise_for_status()
            logger.info(f"Файл {url} загружен на диск")
            return io.BytesIO(await response.read())
    except aiohttp.ClientResponseError as e:
        logger.error(f"Ошибка при скачивание страницы файла: {e}")
        return None
