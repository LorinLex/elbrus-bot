import datetime

from aiogram import html, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InaccessibleMessage

from app import settings
from app.dal import Boy
from app.kb import main_kb


router = Router()


@router.message(CommandStart())
@router.message(F.text == '🏠 Главное меню')
async def start_handler(message: Message, boy: Boy) -> None:
    await message.answer(
        f"Салют, боутишка {html.bold(boy.call_sign)}!",
        reply_markup=main_kb()
    )


@router.message(Command("remaining_time"))
@router.message(F.text == '🧗‍♂️ Сколько осталось до Эльбруса?')
async def remaining_time_handler(message: Message) -> None:
    target_date = datetime.date.fromisoformat(settings.target_date)
    remaining_time = target_date - datetime.date.today()
    await message.answer(
        f"Осталось дней: {html.bold(str(remaining_time.days))}",
        reply_markup=main_kb(),
    )


@router.callback_query(F.data == "fsm_stop")
async def fsm_stop_handler(call: CallbackQuery, state: FSMContext) -> None:
    if call.message is None or isinstance(call.message, InaccessibleMessage):
        await call.answer("Что-то пошло не так:(")
        return

    await call.message.delete()
    await state.clear()
    await call.message.answer(
        text="Окей, ты вернулся в главное меню",
        reply_markup=main_kb()
    )


@router.message()
async def wtf_handler(message: Message) -> None:
    if message.chat.type == "private":
        await message.answer(
            "Моя твоя не понимать",
            reply_markup=main_kb()
        )
