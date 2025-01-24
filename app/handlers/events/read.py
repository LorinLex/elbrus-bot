from dataclasses import asdict
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InaccessibleMessage
from app.dal.events import get_event_list
from app.handlers.events.utils import get_event_caption
from app.kb import event_card_inline_kb
from app.states import MainEventStates


router = Router(name="event_read")


@router.message(F.text == '📋 Посмотреть события')
@router.message(Command("show_events"))
async def read_event_list_handler(message: Message,
                                  state: FSMContext) -> None:
    if isinstance(message, InaccessibleMessage) or message.text is None:
        await message.answer("Что-то пошло не так:(")
        return

    await state.clear()
    await state.set_state(MainEventStates.show)
    await state.update_data(
        start_message=message.message_id
    )

    event_list = await get_event_list()
    for event in event_list:
        # somehow asdict on 'event' not working
        await message.answer_photo(
            photo=event.image,
            caption=get_event_caption(**(asdict(event))),
            reply_markup=event_card_inline_kb(event_id=event.id)
        )
