import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from aiogram.filters import CommandObject
from aiogram.types import Message, User

from src.bot.db.repository import DeadlineRepository
from src.bot.handlers.add import cmd_add


def test_repository_crud_lifecycle():
    async def scenario():
        repo = await DeadlineRepository.from_path(":memory:")
        try:
            d1 = await repo.create(
                user_id=100,
                title="Лаба 5",
                due_date=datetime(2026, 12, 10, 23, 59),
                hours=6.0,
                weight=15.0,
            )
            d2 = await repo.create(
                user_id=100,
                title="Домашка 2",
                due_date=datetime(2026, 12, 3, 18, 0),
                hours=2.0,
                weight=5.0,
            )
            await repo.create(
                user_id=200,
                title="Чужая задача",
                due_date=datetime(2026, 12, 1, 12, 0),
            )

            fetched = await repo.get_by_id(d1.id, user_id=100)
            assert fetched is not None
            assert fetched.title == "Лаба 5"
            assert fetched.hours == 6.0
            assert await repo.get_by_id(d1.id, user_id=200) is None

            items = await repo.list_by_user(100)
            assert [item.id for item in items] == [d2.id, d1.id]

            updated = await repo.update(
                d1.id,
                100,
                title="Лаба 5 (финал)",
                hours=8.0,
                weight=None,
            )
            assert updated is not None
            assert updated.title == "Лаба 5 (финал)"
            assert updated.hours == 8.0
            assert updated.weight is None

            assert await repo.update(d1.id, 200, title="Взлом") is None

            # Добавляем pending-уведомление, чтобы проверить отмену при mark_done
            await repo._conn.execute(
                "INSERT INTO notifications (deadline_id, offset_days, planned_at) VALUES (?, ?, ?)",
                (d2.id, 3, "2026-11-30 09:00:00"),
            )
            await repo._conn.commit()

            done = await repo.mark_done(d2.id, 100)
            assert done is not None
            assert done.status == "completed"
            assert done.completed_at is not None
            assert await repo.mark_done(d2.id, 100) is None

            cursor = await repo._conn.execute(
                "SELECT status FROM notifications WHERE deadline_id = ?", (d2.id,)
            )
            notif = await cursor.fetchone()
            assert notif["status"] == "cancelled"

            active_items = await repo.list_by_user(100, status="active")
            assert [item.id for item in active_items] == [d1.id]

            assert await repo.delete(d1.id, 200) is False
            assert await repo.delete(d1.id, 100) is True
            assert await repo.get_by_id(d1.id) is None
        finally:
            await repo.close()

    asyncio.run(scenario())


def test_cmd_add_persists_to_repository(tmp_path):
    async def scenario():
        db_file = tmp_path / "bot.db"
        repo = await DeadlineRepository.from_path(db_file)
        try:
            message = MagicMock(spec=Message)
            message.from_user = User(
                id=777, is_bot=False, first_name="Андрей", username="kq06"
            )
            message.answer = AsyncMock()
            command = CommandObject(
                prefix="/",
                command="add",
                args="Курсовая | 25.12.2026 20:00 | 12 | 30",
            )

            await cmd_add(message, command, repo=repo)

            items = await repo.list_by_user(777)
            assert len(items) == 1
            assert items[0].title == "Курсовая"
            assert items[0].hours == 12.0
            assert items[0].weight == 30.0
            reply = message.answer.call_args[0][0]
            assert f"Дедлайн №{items[0].id} добавлен" in reply
        finally:
            await repo.close()

    asyncio.run(scenario())
