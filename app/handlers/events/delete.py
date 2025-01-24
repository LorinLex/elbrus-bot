from dataclasses import asdict
from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from app.dal.events import delete_event, get_event
from app.handlers.events.utils import get_event_caption
from app.kb import confirm_delete_inline_kb, main_kb
from app.states import MainEventStates
from app import bot


router = Router(name="event_delete")


@router.callback_query(F.data.startswith("delete_event_"))
async def confirm_delete_event_handler(call: CallbackQuery,
                                       state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    await state.set_state(MainEventStates.delete)

    event_id = call.data[13::]
    event = await get_event(event_id)

    list_start_message = (await state.get_data())["start_message"]
    await bot.delete_messages(
        chat_id=call.message.chat.id,
        message_ids=[*range(list_start_message, call.message.message_id+1)]
    )
    await state.update_data(
        event_id=event_id,
        start_message=call.message.message_id
    )

    await call.message.answer_photo(
        photo=event.image,
        caption=get_event_caption(**(asdict(event)))
    )
    await call.message.answer(
        text="Ты хочешь удалить это событие?",
        reply_markup=confirm_delete_inline_kb()
    )


@router.callback_query(MainEventStates.delete, F.data == ("confirm_yes"))
async def delete_event_handler(call: CallbackQuery,
                               state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    event_id = (await state.get_data())["event_id"]
    await delete_event(event_id)

    await bot.delete_message(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    await call.message.answer(
        text="Событие удалено!",
        reply_markup=main_kb()
    )


@router.callback_query(MainEventStates.delete, F.data == ("confirm_no"))
async def cancel_delete_event_handler(call: CallbackQuery,
                                      state: FSMContext) -> None:
    if call.message is None or call.data is None:
        await call.answer("Что-то пошло не так:(")
        return

    list_start_message = (await state.get_data())["start_message"]
    await bot.delete_messages(
        chat_id=call.message.chat.id,
        message_ids=[*range(list_start_message, call.message.message_id+1)]
    )
    await state.clear()
    await call.message.answer(
        text="Окей, ты вернулся в главное меню",
        show_alert=True,
        reply_markup=main_kb()
    )
