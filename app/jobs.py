from dataclasses import asdict
from datetime import datetime
import logging

from aiogram import html
from app.dal.chat import get_main_group_id
from app.dal.events import get_event_by_id, get_notifying_event_list
from app.dal.sport import get_week_stats
from app.jokes import get_joke
from app.utils import get_event_caption
from app.utils import in_elbrus_height
from . import bot
from aiogram.types import FSInputFile


log = logging.getLogger("jobs")


async def notify_events_remaining_time() -> None:
    event_list = await get_notifying_event_list()
    group_id = await get_main_group_id()

    if not group_id:
        log.error("Нет id группы!!!")
        return

    log.info("Notifying about events")

    if len(event_list) > 0:
        today = datetime.today().date()
        image = FSInputFile("static/firepit.jpg")
        text = "Осталось дней потерпеть до:\n\n"
        for event in event_list:
            timedelta = event.date_start - today
            text += f"{event.name}: {html.bold(str(timedelta.days))}\n"
    else:
        image = FSInputFile("static/angry.jpg")
        text = "Нет запланированных событий... Не надо так." \
               "Быстро взяли и запланировали планы."

    await bot.send_photo(
        chat_id=group_id,
        photo=image,
        caption=text
    )


async def notify_workout_week() -> None:
    group_id = await get_main_group_id()

    if not group_id:
        log.error("Нет id группы!!!")
        return

    rows = await get_week_stats()

    if len(rows) == 0:
        await bot.send_photo(
            chat_id=group_id,
            photo=FSInputFile("static/arni_angry.webp"),
            caption="На этой неделе не было Gym days... "
                    "Не зли Арни, ходи в зал!",
        )
        return

    stats = "".join([
        f"{html.bold(row.call_sign)}: {row.reports_count}, "
        f"прошел {html.bold(str(row.sum_distance))}км ИЛИ "
        f"{in_elbrus_height(row.sum_distance)}% "
        "высоты Эльбруса\n"
        for row in rows
    ])

    await bot.send_photo(
        chat_id=group_id,
        photo=FSInputFile("static/arni_old.webp"),
        caption=f"На этой неделе Gym days:\n{stats}",
    )


async def notify_tommorow_event(event_id: int) -> None:
    group_id = await get_main_group_id()
    if not group_id:
        log.error("Нет id группы!!!")
        return

    event = await get_event_by_id(event_id)
    await bot.send_photo(
        chat_id=group_id,
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )
    await bot.send_message(
        chat_id=group_id,
        text=f"Завтра {html.bold(event.name)}!!!"
    )


async def send_everyday_joke() -> None:
    group_id = await get_main_group_id()
    if not group_id:
        log.error("Нет id группы!!!")
        return

    source, joke = await get_joke()

    if not joke:
        await bot.send_message(
            chat_id=group_id,
            text="Не могу вспомнить анекдот..."
        )
        return

    await bot.send_message(
        chat_id=group_id,
        text="Внимание, анекдот!\n\n"
             f"{joke}\n\n"
             f"Источник: {source}"
    )
