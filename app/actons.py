import logging

from aiogram import html
from app.dal.boys import Boy
from app.dal.chat import get_main_group_id
from app import bot
from aiogram.types import FSInputFile


log = logging.getLogger("actions")


async def send_gym_to_group(boy: Boy) -> None:
    group_id = get_main_group_id()

    if not group_id:
        log.error("Нет id группы!!!")
        return

    await bot.send_photo(
        chat_id=group_id,
        photo=FSInputFile("static/arny_clapping.jpg"),
        caption="Парни!\n"
                f"Сегодня {html.bold(boy.call_sign)} был боссом качалки!\n"
                "Так держать, Железный Арни гордится тобой!\n"
                "Остальным стоит не отставать"
    )
