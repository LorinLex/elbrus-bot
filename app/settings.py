from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import final


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('../.env'),
        env_file_encoding='utf-8'
    )

    debug: bool = True

    bot_token: str = ''

    target_date: str = "2025-08-01"

    sqlite_path: str = ""

    boys: list[dict[str, str]] = []


@lru_cache()
def get_settings() -> Settings:
    return Settings()
