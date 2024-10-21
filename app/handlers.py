import datetime

from aiogram import html, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, InaccessibleMessage, \
    FSInputFile
from aiogram import Router

from app.kb import main_kb, month_kb
from app.models import SportActivity
from app.services import BoysService, SportService
from app.settings import get_settings
from app.db import async_session


router = Router()


@router.message(CommandStart())
@router.message(F.text == '🏠 Главное меню')
async def start_handler(message: Message) -> None:
    if message.from_user is not None:
        await message.answer(
            f"Салют, боутишка {html.bold(message.from_user.first_name)}!",
            reply_markup=main_kb()
        )
    else:
        await message.answer("Салют, боутишка!", reply_markup=main_kb())


@router.message(Command("remaining_time"))
@router.message(F.text == '🧗‍♂️ Сколько осталось до Эльбруса?')
async def remaining_time_handler(message: Message) -> None:
    target_date = datetime.date.fromisoformat(get_settings().target_date)
    remaining_time = target_date - datetime.date.today()
    await message.answer(
        f"Осталось дней: {html.bold(str(remaining_time.days))}",
        reply_markup=main_kb()
    )


@router.message(Command("add_sport_report"))
@router.message(F.text == "🏋️ Похвастаться днем Gym'а")
async def add_sport_report_handler(message: Message) -> None:
    tg_user = message.from_user
    async with async_session() as session:
        if tg_user is None\
                or tg_user.username is None\
                or await BoysService.get_boy(session,
                                             tg_user.username) is None:
            await message.answer("Ты не в списке!!1!!1!")
            return

    await message.answer("Бро, выбери день:", reply_markup=month_kb())


@router.callback_query(F.data.startswith("day_"))
async def write_report(call: CallbackQuery) -> None:
    tg_user = call.from_user
    if call.message is not None\
            and not isinstance(call.message, InaccessibleMessage):
        await call.message.delete()

    async with async_session() as session:
        if tg_user is None\
                or tg_user.username is None:
            await call.answer("Ты не в списке!!1!!1!")
            return

        boy = await BoysService.get_boy(session, tg_user.username)

        if boy is None:
            await call.answer("Ты не в списке!!1!!1!")
            return

        if call.data is None or call.data[4::] == "empty":
            await call.answer(
                "Бро, ты выбрал что-то не то, попробуй снова:",
                reply_markup=month_kb()
            )
            return

        today = datetime.date.today()
        await SportService.add_report(
            session,
            tg_username=tg_user.username,
            date=datetime.date(today.year, today.month, int(call.data[4::]))
        )

        await call.answer("Gym-day записан, бро!", reply_markup=main_kb())

        if call.message is not None\
                and not isinstance(call.message, InaccessibleMessage):
            await call.message.answer_photo(
                photo=FSInputFile("static/arni.jpeg"),
                caption=f"Так и записал: {boy.name} был в Gym'е"
                        f" {call.data[4::]} числа этого месяца.\n"
                        f"Так держать, бро! Арни гордится тобой!",
                reply_markup=main_kb()
            )


@router.message(F.text == "📋 Посмотреть успехи недели")
@router.message(Command("get_week_stats"))
async def show_week_success_handler(message: Message) -> None:
    async with async_session() as session:
        rows = await SportService.get_week_stats(session)
        if len(rows) == 0:
            await message.answer_photo(
                photo=FSInputFile("static/arni_angry.webp"),
                caption="На этой неделе не было Gym days... Не зли Арни, ходи в зал!",
                reply_markup=main_kb()
            )

        answer = "\n".join([f'{html.bold(row[0])}: {row[1]}' for row in rows])

        await message.answer_photo(
            photo=FSInputFile("static/arni_old.webp"),
            caption=f"На этой неделе Gym days:\n{answer}",
            reply_markup=main_kb()
        )


@router.message(F.text == "📋 Посмотреть успехи месяца")
@router.message(Command("get_month_stats"))
async def show_month_success_handler(message: Message) -> None:
    async with async_session() as session:
        rows = await SportService.get_month_stats(session)
        if len(rows) == 0:
            await message.answer_photo(
                photo=FSInputFile("static/arni_angry.webp"),
                caption="В том месяце  не было Gym days... Не зли Арни, ходи в зал!",
                reply_markup=main_kb()
            )

        answer = "\n".join([f'{html.bold(row[0])}: {row[1]}' for row in rows])

        await message.answer_photo(
            photo=FSInputFile("static/arni_old.webp"),
            caption=f"В этом месяце Gym days:\n{answer}",
            reply_markup=main_kb()
        )


@router.message()
async def wtf_handler(message: Message) -> None:
    if message.chat.type == "private":
        await message.answer(
            "Моя твоя не понимать",
            reply_markup=main_kb()
        )
