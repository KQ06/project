from dataclasses import dataclass
from datetime import datetime

DATE_FORMATS = ("%d.%m.%Y %H:%M", "%d.%m.%Y")


class ParseError(ValueError):
    """Ошибка разбора пользовательского ввода."""


@dataclass
class DeadlineInput:
    title: str
    due: datetime
    hours: float | None
    weight: float | None


def _parse_number(raw: str, name: str, low: float, high: float) -> float:
    try:
        value = float(raw.replace(",", "."))
    except ValueError:
        raise ParseError(f"Поле «{name}» должно быть числом")
    if not (low <= value <= high):
        raise ParseError(f"Поле «{name}» должно быть от {low} до {high}")
    return value


def parse_add_args(text: str, now: datetime | None = None) -> DeadlineInput:
    """Разбор аргументов /add: название | дата [ЧЧ:ММ] | часы | вес."""
    now = now or datetime.now()
    parts = [p.strip() for p in text.split("|")]

    if len(parts) < 2 or not parts[0]:
        raise ParseError("Нужно указать название и дату")
    title = parts[0]
    if len(title) > 100:
        raise ParseError("Название не длиннее 100 символов")

    due = None
    for fmt in DATE_FORMATS:
        try:
            due = datetime.strptime(parts[1], fmt)
        except ValueError:
            continue
        if fmt == "%d.%m.%Y":
            due = due.replace(hour=23, minute=59)
        break
    if due is None:
        raise ParseError("Дата в формате ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ")
    if due <= now:
        raise ParseError("Дата уже прошла")

    hours = (
        _parse_number(parts[2], "часы", 0.5, 100)
        if len(parts) > 2 and parts[2]
        else None
    )
    weight = (
        _parse_number(parts[3], "вес", 0, 100)
        if len(parts) > 3 and parts[3]
        else None
    )
    return DeadlineInput(title, due, hours, weight)
