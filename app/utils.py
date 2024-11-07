ELBRUS_HEIGHT: float = 5.642


def in_elbrus_height(dist: float | int) -> float:
    return round(dist / ELBRUS_HEIGHT * 100, 2)
