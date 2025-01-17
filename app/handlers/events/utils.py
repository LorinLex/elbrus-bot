from datetime import date
from aiogram import html
from app.utils import bool2human


def get_event_caption(
    name: str,
    description: str,
    date_start: date,
    length: int,
    author_call_sign: str,
    is_notified_time_left: bool,
    is_repeatable: bool,
    **kwargs
) -> str:
    return (f"{html.bold(name)}\n\n"
            f"{description}\n\n"
            "Когда: "
            f"{html.bold(date_start.strftime('%d.%m.%Y'))}\n"
            "Длится (в днях): "
            f"{html.bold(str(length))}\n"
            "Писать оставшееся время: "
            f"{html.bold(bool2human(is_notified_time_left))}\n"
            "Повторяется каждый год: "
            f"{html.bold(bool2human(is_repeatable))}\n"
            "Автор:"
            f"{html.bold(author_call_sign)}")
