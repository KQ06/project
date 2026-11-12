from datetime import datetime

import pytest

from src.bot.parsing import ParseError, parse_add_args

NOW = datetime(2026, 11, 1, 12, 0)


def test_full_command():
    d = parse_add_args("Лаба 4 | 15.11.2026 23:59 | 6 | 10", now=NOW)
    assert d.title == "Лаба 4"
    assert d.due == datetime(2026, 11, 15, 23, 59)
    assert (d.hours, d.weight) == (6, 10)


def test_date_without_time_defaults_to_end_of_day():
    d = parse_add_args("Лаба | 15.11.2026", now=NOW)
    assert (d.due.hour, d.due.minute) == (23, 59)
    assert d.hours is None and d.weight is None


def test_comma_as_decimal_separator():
    d = parse_add_args("Лаба | 15.11.2026 | 2,5", now=NOW)
    assert d.hours == 2.5


@pytest.mark.parametrize(
    "text",
    [
        "",
        "| 15.11.2026",
        "Лаба",
        "Лаба | завтра",
        "Лаба | 01.10.2026",
        "Лаба | 15.11.2026 | abc",
        "Лаба | 15.11.2026 | 6 | 150",
        "x" * 101 + " | 15.11.2026",
    ],
)
def test_invalid_input(text):
    with pytest.raises(ParseError):
        parse_add_args(text, now=NOW)
