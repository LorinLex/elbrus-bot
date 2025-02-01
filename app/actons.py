from dataclasses import asdict
from enum import Enum
import logging

from aiogram import html
from app.dal.boys import Boy
from app.dal.chat import get_main_group_id
from app import bot
from aiogram.types import FSInputFile

from app.dal.events import EventDB
from app.utils import get_event_caption


log = logging.getLogger("actions")


class EventActionEnum(Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


async def send_gym_to_group(boy: Boy) -> None:
    group_id = await get_main_group_id()

    await bot.send_photo(
        chat_id=group_id,
        photo=FSInputFile("static/arny_clapping.jpg"),
        caption="Парни!\n"
                f"Сегодня {html.bold(boy.call_sign)} был боссом качалки!\n"
                "Так держать, Железный Арни гордится тобой!\n"
                "Остальным стоит не отставать"
    )


async def send_event_action_to_group(type: EventActionEnum,
                                     event: EventDB) -> None:
    group_id = await get_main_group_id()

    match type:
        case EventActionEnum.CREATE:
            text = "Добавлено новое событие!"
        case EventActionEnum.UPDATE:
            text = "Обновлено событие!"
        case EventActionEnum.DELETE:
            text = "Удалено событие!"
        case _:
            return

    await bot.send_photo(
        chat_id=group_id,
        photo=event.image,
        caption=get_event_caption(**asdict(event)),
    )
    await bot.send_message(
        chat_id=group_id,
        text=text
    )
