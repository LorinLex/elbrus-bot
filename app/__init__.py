from app.settings import get_settings
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore


settings = get_settings()
bot = Bot(token=get_settings().bot_token,
          default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
sheduler_ins = AsyncIOScheduler(settings.scheduler_settings)
