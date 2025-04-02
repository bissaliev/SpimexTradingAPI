# SpimexTradingAPI

## О проекте

Spimex Trading API — это микросервисное приложение, предназначенное для работы с данными торгов на Санкт-Петербургской международной товарно-сырьевой бирже (СПбМТСБ). Оно позволяет получать информацию о последних торговых днях, динамике торгов за определенный период, а также фильтровать данные по различным параметрам.

## Стек

- `Python 3.12`
- `FastAPI`
- `PostgreSQL 15`
- `SQLAlchemy 2.0(asyncpg)`
- `Alembic`
- `Redis`
- `fastapi-cache`
- `BeautifulSoup 4`
- `Pandas 2.2`
- `aiohttp 3.11`
- `Docker`

## Основные возможности

- Получение списка последних торговых дней.

- Фильтрация торговых данных по различным параметрам (тип нефтепродукта, база доставки, тип доставки, даты и т. д.).

- Кэширование запросов с использованием Redis.

- Массовое добавление данных о торгах в базу.

## Структура приложения

- `/app/api/`
  - `/routers/` - Директория эндпоинтов
  - `dependencies.py` - Зависимости
- `/app/database/` - Директория конфигураций БД
  - `database.py` - Настройки подключений к БД
  - `models.py` - Содержит модель `SpimexTradingResults`
- `/app/schemas/` - Директория моделей Pydantic
- `/app/services/` - Директория сервисов
- `/app/migrations/` - Директория миграций Alembic
- `/app/parsers/` - Директория запросов и парсинга
  - `parser.py` - Содержит класс `Parser`, который извлекает ссылки со страницы html
  - `scraper.py` - Содержит функции `fetch_page`(Получение страницы) и `fetch_file`(Получение файла)
- `/app/utils/`
  - `redis_client.py` - конфигурации Redis(Кеширование)
  - `file_utils.py` - Содержит класс `XLSExtractor`, который извлекает и отдает нужные данные
- `/app/configs/`
  - `/app/config.py` - Основные настройки проекта
  - `/app/logging_config.py` - Конфигурации логирования
- `.env.example` - Образец файла переменных окружения
- `/app/exceptions.py` - Кастомные классы исключения
- `/app/load_data.py` - Скрипт для загрузки фикстур
- `/app/fixtures.json` - Фикстуры для тестирования API
- `/app/parser_main.py` - Главный модуль для запуска парсинга
- `/app/main.py` - Главный модуль FastAPI
- `/app/tests/` - Директория тестов
- `pytest.ini` - Настройки `Pytest`

## Запуск

- Клонируйте репозиторий:

    ```bash
    git clone git@github.com:bissaliev/SpimexTradingAPI.git
    cd SpimexTradingAPI
    ```

- Создайте файл для переменных окружения(по образцу `.env.example`)

- Запустите `docker compose`:

    ```bash
    docker-compose up --build
    ```

- Выполните миграции в контейнере web:

    ```bash
    docker compose exec web alembic upgrade head
    ```

- Загрузите фикстуры для тестирования API:

    ```bash
    docker compose exec web python3 load_data.py
    ```

## Тестирование

Проект использует библиотеку Pytest для тестирования проекта. Для некоторых тестов понадобится тестовая база данных, развернутая в контейнерах.
Для того чтобы запустить тесты подключите контейнеры для `PostgreSQL` и `Redis`.

- Выполните команду по запуске контейнеров:

    ```bash
    docker compose -f docker-compose.test.yml up --build -d
    ```

  - Или выполните команду makefile:

    ```bash
    make up
    ```

- Выполните запуск тестов командой:

    ```bash
    pytest
    ```

- Чтобы остановить контейнеры выполните команду:

    ```bash
    docker compose -f docker-compose.test.yml down -v
    ```

  - Или выполните команду makefile:

    ```bash
    make down
    ```
