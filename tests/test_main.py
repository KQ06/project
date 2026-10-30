import asyncio
import logging
import subprocess
import sys
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram import Bot, Dispatcher

from src.bot.main import create_dispatcher, main


def test_create_dispatcher():
    dp = create_dispatcher()
    assert isinstance(dp, Dispatcher)


def test_main_logs_bot_started(caplog):
    caplog.set_level(logging.INFO)
    asyncio.run(main())
    assert any("Bot started" in record.message for record in caplog.records)


def test_main_with_mock_bot_and_dispatcher():
    mock_bot = MagicMock(spec=Bot)
    mock_bot.session = MagicMock()
    mock_bot.session.close = AsyncMock()

    mock_dp = MagicMock(spec=Dispatcher)
    mock_dp.start_polling = AsyncMock()

    asyncio.run(main(bot=mock_bot, dp=mock_dp))

    mock_dp.start_polling.assert_awaited_once_with(mock_bot)
    mock_bot.session.close.assert_awaited_once()


def test_main_subprocess_execution():
    result = subprocess.run(
        [sys.executable, "-m", "src.bot.main"],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "Bot started" in combined_output
