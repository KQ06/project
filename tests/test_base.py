import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User
from src.bot.handlers.base import HELP_TEXT, cmd_help, cmd_start


def test_cmd_start_with_user():
    message = MagicMock(spec=Message)
    message.from_user = User(
        id=123, is_bot=False, first_name="Андрей", username="kq06"
    )
    message.answer = AsyncMock()

    asyncio.run(cmd_start(message))

    message.answer.assert_awaited_once()
    called_text = message.answer.call_args[0][0]
    assert "Привет, <b>Андрей</b>" in called_text
    assert "DeadlineBot" in called_text
    assert "/help" in called_text


def test_cmd_start_without_user():
    message = MagicMock(spec=Message)
    message.from_user = None
    message.answer = AsyncMock()

    asyncio.run(cmd_start(message))

    message.answer.assert_awaited_once()
    called_text = message.answer.call_args[0][0]
    assert "Привет, <b>Студент</b>" in called_text


def test_cmd_help():
    message = MagicMock(spec=Message)
    message.answer = AsyncMock()

    asyncio.run(cmd_help(message))

    message.answer.assert_awaited_once_with(HELP_TEXT, parse_mode="HTML")
    assert "/start" in HELP_TEXT
    assert "/add" in HELP_TEXT
    assert "/list" in HELP_TEXT
    assert "/done" in HELP_TEXT
