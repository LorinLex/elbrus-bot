import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.handlers import router

from app.settings import get_settings
from app.db import create_tables, async_session
from app.services import BoysService
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command='start', description='Старт'),
        BotCommand(command='add_sport_report',
                   description="Записать день Gym'а"),
        BotCommand(command='get_week_stats',
                   description="Посмотреть успехи недели"),
        BotCommand(command='get_month_stats',
                   description="Посмотреть успехи месяца"),
        BotCommand(command='remaining_time',
                   description='Узнать сколько осталось до Эльбруса'),
    ]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot: Bot = Bot(token=get_settings().bot_token,
                   default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await set_commands(bot)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    await create_tables()  # TODO: change to alembic
    async with async_session() as session:
        await BoysService.add_boys(session)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
