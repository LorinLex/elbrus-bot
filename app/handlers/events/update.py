import re
from datetime import datetime
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from app import bot
from app.dal.events import update_event, get_event_by_id
from app.handlers.events.utils import get_event_caption
from app.kb import confirm_inline_kb, stop_fsm_inline_kb, \
    update_event_inline_kb
from app.sheduler import modify_sheduled_event_date
from app.states import UpdateEventStates, MainEventStates
from app.utils import human2bool
from dataclasses import asdict


router = Router(name="event_update")


@router.callback_query(F.data.startswith("update_event_"),
                       F.message.chat.type == "private")
async def update_event_handler(call: CallbackQuery,
                               state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    await state.set_state(MainEventStates.update)

    event_id = call.data[13::]
    event = await get_event_by_id(event_id)

    try:
        list_start_message = (await state.get_data())["start_message"]
        await bot.delete_messages(
            chat_id=call.message.chat.id,
            message_ids=[*range(list_start_message, call.message.message_id+1)]
        )
    except KeyError:
        pass

    await state.update_data(
        event_id=event_id,
        start_message=call.message.message_id
    )

    await call.message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event))),
        reply_markup=update_event_inline_kb()
    )


@router.callback_query(MainEventStates.update, F.data.startswith("update_"))
async def update_event_data_request_handler(call: CallbackQuery,
                                            state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    message_dict = {
        "name": "Напиши новое название",
        "image": "Отправь новую картинку",
        "description": "Напиши новое описание",
        "date_start": "Введи новую дату старта",
        "length": "Напиши продолжительность",
        "is_notified_time_left": "Уведомлять сколько осталось времени?",
        "is_repeatable": "Повторять каждый год?",
    }

    kb_list = {
        "name": stop_fsm_inline_kb,
        "image": stop_fsm_inline_kb,
        "description": stop_fsm_inline_kb,
        "date_start": stop_fsm_inline_kb,
        "length": stop_fsm_inline_kb,
        "is_notified_time_left": confirm_inline_kb,
        "is_repeatable": confirm_inline_kb
    }

    field_name = call.data[7::]

    await state.set_state(getattr(UpdateEventStates, field_name))
    await call.message.answer(
        text=message_dict[field_name],
        reply_markup=kb_list[field_name]()
    )


@router.message(UpdateEventStates.name)
async def update_event_name_handler(message: Message,
                                    state: FSMContext) -> None:
    if message.text is None:
        await message.answer(
            text="Что-то пошло не так:(",
        )
        return

    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[*range(list_start_message, message.message_id+1)]
    )

    await update_event(event_id=state_data["event_id"], name=message.text)
    event = await get_event_by_id(state_data["event_id"])
    await message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await message.answer(
        text="Событие обновлено!"
    )


@router.message(UpdateEventStates.image)
async def update_event_image_handler(message: Message,
                                     state: FSMContext) -> None:
    file_id = message.photo[-1].file_id  # type: ignore

    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[*range(list_start_message, message.message_id+1)]
    )

    await update_event(event_id=state_data["event_id"], image=file_id)
    event = await get_event_by_id(state_data["event_id"])
    await message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await message.answer(
        text="Событие обновлено!"
    )


@router.message(UpdateEventStates.description)
async def update_event_description_handler(message: Message,
                                           state: FSMContext) -> None:
    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[*range(list_start_message, message.message_id+1)]
    )

    await update_event(
        event_id=state_data["event_id"],
        description=message.text
    )
    event = await get_event_by_id(state_data["event_id"])
    await message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await message.answer(
        text="Событие обновлено!"
    )


@router.message(UpdateEventStates.date_start)
async def update_event_date_start_handler(message: Message,
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

    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[*range(list_start_message, message.message_id+1)]
    )

    await update_event(event_id=state_data["event_id"], date_start=date)
    event = await get_event_by_id(state_data["event_id"])

    modify_sheduled_event_date(event)

    await message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await message.answer(
        text="Событие обновлено!"
    )


@router.message(UpdateEventStates.length)
async def update_event_length_handler(message: Message,
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

    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=message.chat.id,
        message_ids=[*range(list_start_message, message.message_id+1)]
    )

    await update_event(event_id=state_data["event_id"], length=length)
    event = await get_event_by_id(state_data["event_id"])
    await message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await message.answer(
        text="Событие обновлено!"
    )


@router.callback_query(UpdateEventStates.is_notified_time_left,
                       F.data.startswith("confirm_"))
async def update_event_notify_handler(call: CallbackQuery,
                                      state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=call.message.chat.id,
        message_ids=[*range(list_start_message, call.message.message_id+1)]
    )

    await update_event(
        event_id=state_data["event_id"],
        is_notified_time_left=human2bool(call.data[8::])
    )
    event = await get_event_by_id(state_data["event_id"])
    await call.message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await call.message.answer(
        text="Событие обновлено!"
    )


@router.callback_query(UpdateEventStates.is_repeatable,
                       F.data.startswith("confirm_"))
async def update_event_repeatable_handler(call: CallbackQuery,
                                          state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    state_data = await state.get_data()
    await state.clear()

    list_start_message = state_data["start_message"]
    await bot.delete_messages(
        chat_id=call.message.chat.id,
        message_ids=[*range(list_start_message, call.message.message_id+1)]
    )

    await update_event(
        event_id=state_data["event_id"],
        is_repeatable=human2bool(call.data[8::])
    )
    event = await get_event_by_id(state_data["event_id"])
    await call.message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )

    await call.message.answer(
        text="Событие обновлено!"
    )
