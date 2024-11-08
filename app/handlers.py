import datetime
import re

from aiogram import html, F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteMessages
from aiogram.types import Message, CallbackQuery, InaccessibleMessage, \
    FSInputFile

from app.app import settings, bot
from app.dal import Boy, add_report, get_month_stats, get_week_stats
from app.kb import confirm_inline_kb, main_kb, month_kb, stop_fsm_inline_kb
from app.states import AddSportReportStates
from app.utils import in_elbrus_height


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


@router.message(Command("add_sport_report"))
@router.message(F.text == "🏋️ Похвастаться днем Gym'а")
async def add_sport_report_handler(message: Message,
                                   state: FSMContext) -> None:
    await state.clear()
    await message.answer("Бро, выбери день:", reply_markup=month_kb())
    await state.set_state(AddSportReportStates.day)


@router.callback_query(AddSportReportStates.day, F.data.startswith("day_"))
async def write_day(call: CallbackQuery, state: FSMContext) -> None:
    if call.message is None:
        await call.answer("Что-то пошло не так:(")
        return

    if call.message is not None\
            and not isinstance(call.message, InaccessibleMessage):
        await call.message.delete()

    if call.data is None or call.data[4::] == "empty":
        await state.clear()
        await state.set_state(AddSportReportStates.day)
        await call.message.answer(
            "Бро, ты выбрал что-то не то, попробуй снова:",
            reply_markup=month_kb()
        )
        return

    await state.set_data({"date": call.data[4::]})
    await state.set_state(AddSportReportStates.distance)
    await call.message.answer(
        text="Гуд!\n"
             "А теперь, если ты бегал или ходил, напиши мне расстояние\n"
             "Или нуль",
        reply_markup=stop_fsm_inline_kb()
    )


@router.message(AddSportReportStates.distance)
async def write_distance(message: Message,
                         state: FSMContext,
                         boy: Boy) -> None:
    await DeleteMessages(
        chat_id=message.chat.id,
        message_ids=[message.message_id, message.message_id-1]
    ).as_(bot=bot)

    if message.text is None:
        await message.answer("Что-то пошло не так:(",
                             reply_markup=stop_fsm_inline_kb())
        return

    distance = re.match(pattern=r'^\d{0,3}(?:[\.,]\d{0,3})?$',
                        string=message.text)
    if distance is None:
        await message.answer("Ты не правильно ввел, попробуй снова",
                             reply_markup=stop_fsm_inline_kb())
        return

    report = await state.get_data()
    if message.text is not None:
        await state.set_data({**report, "distance": message.text})

    await state.set_state(AddSportReportStates.confirm)
    await message.answer(
        text=(
            f"Значит {html.bold(boy.call_sign)} был в Gym'е "
            f"{html.bold(report['date'])} числа этого месяца, и преодолел "
            f"{html.bold(message.text)}км.\n"
            "Все верно?"
        ),
        reply_markup=confirm_inline_kb()
    )


@router.callback_query(AddSportReportStates.confirm, F.data == "confirm_yes")
async def write_report(call: CallbackQuery,
                       state: FSMContext,
                       boy: Boy) -> None:
    report = await state.get_data()
    today = datetime.date.today()

    await add_report(
        tg_username=boy.tg_username,
        date=datetime.date(today.year, today.month, int(report["date"])),
        distance=float(report["distance"])
    )

    await state.clear()
    await call.answer("Gym-day записан, бро!", reply_markup=main_kb())

    if call.message is not None\
            and not isinstance(call.message, InaccessibleMessage):
        await call.message.delete()
        await call.message.answer_photo(
            photo=FSInputFile("static/arni.jpeg"),
            caption=(
                "Так и записал:\n"
                f"{html.bold(boy.name)} был в Gym'е "
                f"{html.bold(report['date'])} числа этого месяца и "
                f"преодолел {html.bold(report['distance'])}км.\n"
                "Так держать, бро! Арни гордится тобой!"
            ),
            reply_markup=main_kb()
        )


@router.callback_query(AddSportReportStates.confirm, F.data == "confirm_no")
async def retry_add_sport_report_handler(call: CallbackQuery,
                                         state: FSMContext) -> None:
    if call.message is None:
        await call.answer("Что-то пошло не так:(")
        return

    if not isinstance(call.message, InaccessibleMessage):
        await call.message.delete()

    await state.clear()
    await state.set_state(AddSportReportStates.day)
    await call.message.answer("Бро, заново выбери день:",
                              reply_markup=month_kb())


@router.message(F.text == "📋 Посмотреть успехи недели")
@router.message(Command("get_week_stats"))
async def show_week_success_handler(message: Message) -> None:
    rows = await get_week_stats()
    if len(rows) == 0:
        await message.answer_photo(
            photo=FSInputFile("static/arni_angry.webp"),
            caption="На этой неделе не было Gym days... "
                    "Не зли Арни, ходи в зал!",
            reply_markup=main_kb()
        )

    stats = "".join([
        f"{html.bold(row.call_sign)}: {row.reports_count}, "
        f"прошел {html.bold(str(row.sum_distance))}км ИЛИ "
        f"{in_elbrus_height(row.sum_distance)}% "
        "высоты Эльбруса\n"
        for row in rows
    ])

    await message.answer_photo(
        photo=FSInputFile("static/arni_old.webp"),
        caption=f"На этой неделе Gym days:\n{stats}",
        reply_markup=main_kb()
    )
    await message.answer(
        "P.S. Дистанция от Эльбруса считается по прямой, перпендикулярной "
        "центру земли, маршрут кратно больше!"
    )


@router.message(F.text == "📋 Посмотреть успехи месяца")
@router.message(Command("get_month_stats"))
async def show_month_success_handler(message: Message) -> None:
    rows = await get_month_stats()
    if len(rows) == 0:
        await message.answer_photo(
            photo=FSInputFile("static/arni_angry.webp"),
            caption="В этом месяце не было Gym days... "
                    "Не зли Арни, ходи в зал!",
            reply_markup=main_kb()
        )

    stats = "".join([
        f"{html.bold(row.call_sign)}: {row.reports_count}, "
        f"прошел {html.bold(str(row.sum_distance))}км ИЛИ "
        f"{in_elbrus_height(row.sum_distance)}% "
        "высоты Эльбруса\n"
        for row in rows
    ])
    await message.answer_photo(
        photo=FSInputFile("static/arni_old.webp"),
        caption=f"В этом месяце Gym days:\n{stats}",
        reply_markup=main_kb()
    )


@router.callback_query(AddSportReportStates.day, F.data == "fsm_stop")
@router.callback_query(AddSportReportStates.distance, F.data == "fsm_stop")
@router.callback_query(AddSportReportStates.confirm, F.data == "fsm_stop")
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
