from datetime import date
from aiogram import html


ELBRUS_HEIGHT: float = 5.642


def in_elbrus_height(dist: float | int) -> float:
    return round(dist / ELBRUS_HEIGHT * 100, 2)


def bool2human(var: bool) -> str:
    return "Да" if var else "Нет"


def human2bool(var: str) -> bool:
    match var.lower():
        case "да" | "yes":
            return True
        case "нет" | "no":
            return False
        case _:
            raise ValueError


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

