from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext


async def update_state(state: FSMContext, new_state: State, **kwargs) -> None:
    state_data = await state.get_data()
    await state.set_data({**state_data, **kwargs})
    await state.set_state(new_state)


class AddSportReportStates(StatesGroup):
    day = State()
    distance = State()
    confirm = State()


class MainEventStates(StatesGroup):
    """Группа состояний для просмотра и удаления событий."""
    show = State()
    delete = State()  # для подтверждения


class CreateEventStates(StatesGroup):
    """
    Группа состояний для создания нового события в БД.
    Для исправления данных перед записью используется FixEventStates.
    """
    name = State()
    image = State()
    description = State()
    date_start = State()
    length = State()
    is_notified_time_left = State()
    is_repeatable = State()
    confirm = State()


class FixEventStates(StatesGroup):
    """Группа состояний для исправления поля перед записью события в БД."""
    name = State()
    image = State()
    description = State()
    date_start = State()
    length = State()
    is_notified_time_left = State()
    is_repeatable = State()


class UpdateEventStates(StatesGroup):
    """Группа состояний для обновления полей события, записанного в БД."""
    name = State()
    image = State()
    description = State()
    date_start = State()
    length = State()
    is_notified_time_left = State()
    is_repeatable = State()
    confirm = State()
