import re
from datetime import datetime
from aiogram import html, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app import bot
from app.actons import EventActionEnum, send_event_action_to_group
from app.dal import Boy
from app.dal.events import Event, add_event, get_event_by_name
from app.utils import get_event_caption
from app.kb import confirm_inline_kb, \
    main_kb, stop_fsm_inline_kb
from app.sheduler import shedule_new_event
from app.states import CreateEventStates
from sqlalchemy.exc import NoResultFound


router = Router(name="event_create")


@router.message(Command("add_event"), F.chat.type == "private")
@router.message(F.text == "🏕 Добавить событие", F.chat.type == "private")
async def add_event_handler(message: Message,
                            state: FSMContext,
                            boy: Boy) -> None:
    await state.clear()
    await state.set_state(CreateEventStates.name)
    await state.update_data(
        author_call_sign=boy.call_sign,
        start_message=message.message_id
    )
    await message.answer(
        text="Круто, давай добавим новое событие!\n"
             "Напиши как оно называется",
        reply_markup=stop_fsm_inline_kb()
    )


@router.message(CreateEventStates.name)
async def add_event_name_handler(message: Message, state: FSMContext) -> None:
    if message.text is None:
        await message.answer(
            text="Что-то пошло не так:(",
        )
        return

    try:
        await get_event_by_name(name=message.text)
        await message.answer(
            text="Такое название уже есть, попробуй снова!",
            reply_markup=stop_fsm_inline_kb()
        )
        return
    except NoResultFound:
        pass

    await state.update_data(name=message.text)
    await state.set_state(CreateEventStates.image)
    await message.answer(
        text="Теперь отправь мне картинку события",
        reply_markup=stop_fsm_inline_kb()
    )


@router.message(CreateEventStates.image)
async def add_event_image_handler(message: Message, state: FSMContext) -> None:
    file_id = message.photo[-1].file_id  # type: ignore
    await state.update_data(image=file_id)
    await state.set_state(CreateEventStates.description)
    await message.answer(
        text="А теперь напиши краткое описание",
        reply_markup=stop_fsm_inline_kb()
    )


@router.message(CreateEventStates.description)
async def add_event_description_handler(message: Message,
                                        state: FSMContext) -> None:
    if message.text is None:
        await message.answer(
            text="Что-то пошло не так:(",
        )
        return

    await state.update_data(description=message.text)
    await state.set_state(CreateEventStates.date_start)
    await message.answer(
        text="Мне нужно узнать когда будет событие.\n"
             f"Напиши в формате {html.bold('ДД.ММ.ГГГГ')}",
        reply_markup=stop_fsm_inline_kb()
    )


@router.message(CreateEventStates.date_start)
async def add_event_date_start_handler(message: Message,
                                       state: FSMContext) -> None:
    if message.text is None:
        await message.answer(
            text="Что-то пошло не так:(",
        )
        return

    try:
        date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer(
            text="Ты ввел не правильно, попробуй еще раз",
            reply_markup=stop_fsm_inline_kb()
        )
        return

    await state.update_data(date_start=date)
    await state.set_state(CreateEventStates.length)
    await message.answer(
        text="А сколько дней оно будет длится?",
        reply_markup=stop_fsm_inline_kb()
    )


@router.message(CreateEventStates.length)
async def add_event_length_handler(message: Message,
                                   state: FSMContext) -> None:
    if message.text is None:
        await message.answer(
            text="Что-то пошло не так:(",
        )
        return

    length = re.match(pattern=r'^\d\d?\d?$', string=message.text)

    if length is None:
        await message.answer(
            text="Как-то странно, попробуй еще раз",
            reply_markup=stop_fsm_inline_kb()
        )
        return

    await state.update_data({"length": message.text})
    await state.set_state(CreateEventStates.is_notified_time_left)
    await message.answer(
        text="Об оставшемся кол-ве дней я пишу в чат.\n"
             "Нужно ли писать и об этом?",
        reply_markup=confirm_inline_kb()
    )


@router.callback_query(CreateEventStates.is_notified_time_left,
                       F.data.startswith("confirm_"))
async def add_event_notify_handler(call: CallbackQuery,
                                   state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    await state.update_data(
        is_notified_time_left=True if call.data[8::] == "yes" else False
    )
    await state.set_state(CreateEventStates.is_repeatable)
    await call.message.answer(
        text="А это событие будет повторяться ежегодно?",
        reply_markup=confirm_inline_kb()
    )


@router.callback_query(CreateEventStates.is_repeatable,
                       F.data.startswith("confirm_"))
async def add_event_repeatable_handler(call: CallbackQuery,
                                       state: FSMContext,
                                       boy: Boy) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    state_data = await state.get_data()
    await state.clear()
    is_repeatable = True if call.data[8::] == "yes" else False

    new_event = Event(
        name=state_data["name"],
        description=state_data["description"],
        date_start=state_data["date_start"],
        length=state_data["length"],
        author_call_sign=boy.call_sign,
        is_notified_time_left=state_data["is_notified_time_left"],
        is_repeatable=is_repeatable,
        image=state_data["image"],
    )
    await add_event(new_event)

    event_obj = await get_event_by_name(name=state_data["name"])
    await send_event_action_to_group(EventActionEnum.CREATE, event_obj)
    shedule_new_event(event=event_obj)

    await bot.delete_messages(
        chat_id=call.from_user.id,
        message_ids=[*range(state_data["start_message"]+1,
                            call.message.message_id+1)]
    )

    await call.message.answer_photo(
        photo=state_data["image"],
        caption=get_event_caption(**state_data, is_repeatable=is_repeatable),
    )
    await call.message.answer(
        text="Событие добавлено!",
        reply_markup=main_kb()
    )
