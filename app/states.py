from aiogram.fsm.state import StatesGroup, State


class AddSportReportStates(StatesGroup):
    day = State()
    distance = State()
    confirm = State()
