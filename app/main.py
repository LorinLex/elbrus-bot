import asyncio
import logging
import sys

from app.dal import add_boys
from app.dal.events import get_future_event_list
from app.handlers import main_router, sport_router, event_router
from app.jobs import notify_events_remaining_time, \
    notify_tommorow_event, notify_workout_week
from app.middlewares import ChatWritingMiddleware, ManCheckingMiddleware
from app import bot, dp, settings
from app.db import db_manager
from aiogram.types import BotCommand, BotCommandScopeAllGroupChats, \
    BotCommandScopeAllPrivateChats
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger


async def set_commands():
    private_commands = [
        BotCommand(command='start', description='Старт'),
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


async def start_sheduler() -> None:
    sheduler = AsyncIOScheduler(settings.scheduler_settings)
    sheduler.add_job(
        notify_events_remaining_time,
        trigger=settings.notify_event_trigger
    )
    sheduler.add_job(
        notify_workout_week,
        trigger=settings.notify_workout_week_trigger
    )

    event_list = await get_future_event_list()
    for event in event_list:
        sheduler.add_job(
            notify_tommorow_event,
            kwargs={"event_id": event.id},
            trigger=DateTrigger(run_date=event.date_start,
                                timezone="Europe/Moscow")
        )

    sheduler.start()


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
