import asyncio
import logging
import sys

from app.handlers import router
from app.db import create_tables, async_session
from app.services import BoysService
from app.app import bot, dp, settings
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_commands():
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


async def start_bot():
    await set_commands()
    await create_tables()
    async with async_session() as session:
        await BoysService.add_boys(session)


async def main() -> None:
    dp.include_router(router)
    dp.startup.register(start_bot)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format='%(asctime)s:%(levelname)s:%(name)s - %(message)s',
        stream=sys.stdout
    )
    asyncio.run(main())
