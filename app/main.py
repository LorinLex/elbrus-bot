import asyncio
import logging
import sys

from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, \
    BotCommandScopeAllPrivateChats
from app import bot, dp, settings
from app.dal import add_boys
from app.db import db_manager
from app.handlers import main_router, sport_router, event_router
from app.middlewares import ChatWritingMiddleware, ManCheckingMiddleware
from app.sheduler import start_sheduler


async def set_commands():
    private_commands = [
        BotCommand(command='start', description='Старт'),
        BotCommand(command='joke', description='Вспомнить анекдот'),
        BotCommand(command='add_sport_report',
                   description="Записать день Gym'а"),
        BotCommand(command='add_event',
                   description="Добавить событие"),
        BotCommand(command='show_events',
                   description="Посмотреть список событий"),
        BotCommand(command='get_week_stats',
                   description="Посмотреть успехи недели"),
        BotCommand(command='get_month_stats',
                   description="Посмотреть успехи месяца"),
        BotCommand(command='remaining_time',
                   description='Узнать сколько осталось до Эльбруса'),
    ]

    group_commands = [
        BotCommand(command='start', description='Старт'),
        BotCommand(command='joke', description='Вспомнить анекдот'),
        BotCommand(command='show_events',
                   description="Посмотреть список событий"),
        BotCommand(command='get_week_stats',
                   description="Посмотреть успехи недели"),
        BotCommand(command='get_month_stats',
                   description="Посмотреть успехи месяца"),
        BotCommand(command='remaining_time',
                   description='Узнать сколько осталось до Эльбруса'),
    ]
    await bot.set_my_commands(
        private_commands,
        BotCommandScopeAllPrivateChats()
    )

    await bot.set_my_commands(
        group_commands,
        BotCommandScopeAllGroupChats()
    )


def register_midddlewares() -> None:
    dp.message.middleware.register(ManCheckingMiddleware())
    dp.callback_query.middleware.register(ManCheckingMiddleware())

    dp.message.middleware.register(ChatWritingMiddleware())
    dp.callback_query.middleware.register(ChatWritingMiddleware())


async def start_bot():
    await set_commands()
    await db_manager.init_models()
    await add_boys()


async def main() -> None:
    dp.include_routers(sport_router, event_router, main_router)
    dp.startup.register(start_bot)
    register_midddlewares()
    await start_sheduler()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format='%(asctime)s:%(levelname)s:%(name)s - %(message)s',
        stream=sys.stdout
    )
    asyncio.run(main())
