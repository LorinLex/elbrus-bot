import datetime
import logging

from aiogram import html
from aiogram.filters import  Command
from aiogram.types import Message
from aiogram import Router

from app.settings import get_settings


router = Router()


@router.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """
    This handler receives messages with `/start` command
    """
    if message.from_user is not None:
        await message.answer(f"Салют, боутишка {html.bold(message.from_user.first_name)}!")
    else:
        await message.answer("Салют, боутишка!")


@router.message(Command("remaining_time"))
async def remaining_time_handler(message: Message) -> None:
    target_date = datetime.date.fromisoformat(get_settings().target_date)
    remaining_time = target_date - datetime.date.today()
    await message.answer(f"Осталось дней: {html.bold(str(remaining_time.days))}")


@router.message()
async def wtf_handler(message: Message) -> None:
    if message.chat.type == "private":
        await message.answer("Моя твоя не понимать")
