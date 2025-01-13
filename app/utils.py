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
