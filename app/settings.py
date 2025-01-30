from apscheduler.triggers.cron import CronTrigger  # type: ignore
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import final


@final
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=('../.env'),
        env_file_encoding='utf-8'
    )

    debug: bool = True

    bot_token: str = ''

    scheduler_settings: dict[str, str | dict[str, str]] = {
        'apscheduler.job_defaults.coalesce': 'false',
        'apscheduler.job_defaults.max_instances': '3',
    }

    notify_event_trigger: CronTrigger = CronTrigger(day_of_week="fri", hour=19)
    notify_workout_week_trigger: CronTrigger = CronTrigger(day_of_week="sun", 
                                                           hour=19)

    target_date: str = "2025-08-01"

    sqlite_path: str = ""

    boys: list[dict[str, str]] = []


@lru_cache()
def get_settings() -> Settings:
    return Settings()
