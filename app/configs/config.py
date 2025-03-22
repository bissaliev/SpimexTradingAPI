from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_DIR: Path = Path(__file__).parent.parent
    POSTGRES_DB: str
    DB_HOST: str
    DB_PORT: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env")

    def get_db_postgres_url(self):
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"

    def get_db_sqlite_url(self):
        return "sqlite+aiosqlite:///db.sqlite3"


settings = Settings()
