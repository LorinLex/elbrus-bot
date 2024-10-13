from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import final


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('.prod.env', '.dev.env'),
        env_file_encoding='utf-8'
    )

    debug: bool = True

    bot_token: str = ''

    target_date: str = "1-08-2025"


@lru_cache()  # get it from memory
def get_settings() -> Settings:
    return Settings()
