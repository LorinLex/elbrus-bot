import datetime
from calendar import monthrange
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_kb() -> ReplyKeyboardMarkup:
    kb_list = [
        [KeyboardButton(text="🏋️ Похвастаться днем Gym'а")],
        [KeyboardButton(text="📋 Посмотреть успехи недели")],
        [KeyboardButton(text="📋 Посмотреть успехи месяца")],
        [KeyboardButton(text="🧗‍♂️ Сколько осталось до Эльбруса?")]
    ]
    return ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню👇"
    )


def month_kb() -> InlineKeyboardMarkup:
    today = datetime.date.today()
    month_days_count = monthrange(today.year, today.month)[1]
    month_start_weekday = datetime.date(today.year, today.month, 1).\
        isocalendar()[2]
    month_end_weekday = datetime.date(today.year,
                                      today.month,
                                      month_days_count).isocalendar()[2]

    builder = InlineKeyboardBuilder()

    builder.add(InlineKeyboardButton(text="Сегодня",
                                     callback_data=f"day_{today.day}"))

    if month_start_weekday != 1:
        for i in range(1, month_start_weekday):
            builder.add(InlineKeyboardButton(text=" ",
                                             callback_data="day_empty"))

    for day in range(1, month_days_count):
        builder.add(InlineKeyboardButton(text=str(day),
                                         callback_data=f"day_{day}"))

    if month_end_weekday != 7:
        for i in range(month_end_weekday, 8):
            builder.add(InlineKeyboardButton(text=" ",
                                             callback_data="day_empty"))

    builder.add(InlineKeyboardButton(text="❌ Отмена ❌",
                                     callback_data="fsm_stop"))
    #  WARNING: Если февраль начинается с пн, и год не високосный
    # - может не красиво отобразиться
    builder.adjust(1, 7, 7, 7, 7, 7, 1)

    return builder.as_markup()


def confirm_inline_kb() -> InlineKeyboardMarkup:
    kb_list = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data="confirm_yes"),
            InlineKeyboardButton(text="⛔️ Нет", callback_data="confirm_no")
        ],
        [InlineKeyboardButton(text="❌ Отмена ❌", callback_data="fsm_stop")]
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Воспользуйся меню"
    )


def stop_fsm_inline_kb() -> InlineKeyboardMarkup:
    kb_list = [
        [InlineKeyboardButton(text="❌ Отмена ❌", callback_data="fsm_stop")],
    ]

    return InlineKeyboardMarkup(
        inline_keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True
    )
