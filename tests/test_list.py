import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from aiogram.types import CallbackQuery, Message, User

from src.bot.db.repository import DeadlineRepository
from src.bot.handlers.list import cb_list_page, cmd_list

NOW = datetime(2026, 11, 26, 12, 0)


def test_cmd_list_empty():
    async def scenario():
        repo = await DeadlineRepository.from_path(":memory:")
        try:
            message = MagicMock(spec=Message)
            message.from_user = User(id=1, is_bot=False, first_name="Андрей")
            message.answer = AsyncMock()

            await cmd_list(message, repo=repo, now=NOW)

            text = message.answer.call_args[0][0]
            assert "Дедлайнов нет 🎉" in text
        finally:
            await repo.close()

    asyncio.run(scenario())


def test_cmd_list_sorted_with_remaining_and_only_active():
    async def scenario():
        repo = await DeadlineRepository.from_path(":memory:")
        try:
            d_late = await repo.create(
                1, "Курсовая <AI>", NOW + timedelta(days=5, hours=3)
            )
            d_soon = await repo.create(1, "Лаба 5", NOW + timedelta(hours=6))
            d_done = await repo.create(1, "Сданная задача", NOW + timedelta(days=1))
            await repo.mark_done(d_done.id, 1)
            await repo.create(2, "Чужая задача", NOW + timedelta(days=1))

            message = MagicMock(spec=Message)
            message.from_user = User(id=1, is_bot=False, first_name="Андрей")
            message.answer = AsyncMock()

            await cmd_list(message, repo=repo, now=NOW)

            text = message.answer.call_args[0][0]
            kwargs = message.answer.call_args[1]
            assert kwargs["reply_markup"] is None
            assert "Активные дедлайны (2)" in text
            assert f"№{d_soon.id}" in text
            assert f"№{d_late.id}" in text
            assert "Курсовая &lt;AI&gt;" in text
            assert "осталось 6 ч" in text
            assert "осталось 5 дн. 3 ч" in text
            assert "Сданная задача" not in text
            assert "Чужая задача" not in text
            assert text.index("Лаба 5") < text.index("Курсовая &lt;AI&gt;")
        finally:
            await repo.close()

    asyncio.run(scenario())


def test_cmd_list_pagination_over_ten_items():
    async def scenario():
        repo = await DeadlineRepository.from_path(":memory:")
        try:
            for idx in range(1, 14):
                await repo.create(
                    1,
                    f"Задача {idx:02d}",
                    NOW + timedelta(days=idx),
                )

            message = MagicMock(spec=Message)
            message.from_user = User(id=1, is_bot=False, first_name="Андрей")
            message.answer = AsyncMock()

            await cmd_list(message, repo=repo, now=NOW)

            page1_text = message.answer.call_args[0][0]
            page1_kb = message.answer.call_args[1]["reply_markup"]
            assert "Активные дедлайны (13)" in page1_text
            assert "Страница 1 из 2" in page1_text
            assert "Задача 10" in page1_text
            assert "Задача 11" not in page1_text
            assert page1_kb is not None
            cb_values = [b.callback_data for b in page1_kb.inline_keyboard[0]]
            assert "list_page:2" in cb_values

            callback = MagicMock(spec=CallbackQuery)
            callback.from_user = User(id=1, is_bot=False, first_name="Андрей")
            callback.data = "list_page:2"
            callback.message = MagicMock(spec=Message)
            callback.message.edit_text = AsyncMock()
            callback.answer = AsyncMock()

            await cb_list_page(callback, repo=repo, now=NOW)

            page2_text = callback.message.edit_text.call_args[0][0]
            page2_kb = callback.message.edit_text.call_args[1]["reply_markup"]
            assert "Страница 2 из 2" in page2_text
            assert "Задача 11" in page2_text
            assert "Задача 13" in page2_text
            assert "Задача 01" not in page2_text
            cb_values_2 = [b.callback_data for b in page2_kb.inline_keyboard[0]]
            assert "list_page:1" in cb_values_2
            callback.answer.assert_awaited_once()
        finally:
            await repo.close()

    asyncio.run(scenario())
