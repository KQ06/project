from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import aiosqlite

from src.bot.db.database import init_db

_UNSET: Any = object()


@dataclass(frozen=True)
class Deadline:
    id: int
    user_id: int
    title: str
    due_date: datetime
    hours: float | None = None
    weight: float | None = None
    status: str = "active"
    completed_at: datetime | None = None
    created_at: datetime | None = None


def _row_to_deadline(row: aiosqlite.Row) -> Deadline:
    return Deadline(
        id=row["id"],
        user_id=row["user_id"],
        title=row["title"],
        due_date=datetime.fromisoformat(row["due_date"]),
        hours=row["hours"],
        weight=row["weight"],
        status=row["status"],
        completed_at=(
            datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None
        ),
        created_at=(
            datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
        ),
    )


class DeadlineRepository:
    """Асинхронный репозиторий CRUD-операций для пользователей и дедлайнов."""

    def __init__(self, conn: aiosqlite.Connection) -> None:
        self._conn = conn

    @classmethod
    async def from_path(cls, db_path: str | Path) -> "DeadlineRepository":
        conn = await init_db(db_path)
        return cls(conn)

    async def close(self) -> None:
        await self._conn.close()

    async def ensure_user(
        self,
        user_id: int,
        username: str | None = None,
        first_name: str | None = None,
    ) -> None:
        """Создать или обновить профиль пользователя Telegram."""
        await self._conn.execute(
            """
            INSERT INTO users (user_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(excluded.username, users.username),
                first_name = COALESCE(excluded.first_name, users.first_name)
            """,
            (user_id, username, first_name),
        )
        await self._conn.commit()

    async def create(
        self,
        user_id: int,
        title: str,
        due_date: datetime,
        hours: float | None = None,
        weight: float | None = None,
    ) -> Deadline:
        """Создать новый дедлайн и вернуть сохранённую запись."""
        await self.ensure_user(user_id)
        cursor = await self._conn.execute(
            """
            INSERT INTO deadlines (user_id, title, due_date, hours, weight)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                title,
                due_date.isoformat(sep=" ", timespec="seconds"),
                hours,
                weight,
            ),
        )
        await self._conn.commit()
        created = await self.get_by_id(cursor.lastrowid)
        assert created is not None
        return created

    async def get_by_id(
        self, deadline_id: int, user_id: int | None = None
    ) -> Deadline | None:
        """Получить дедлайн по идентификатору (с опциональной проверкой владельца)."""
        if user_id is None:
            cursor = await self._conn.execute(
                "SELECT * FROM deadlines WHERE id = ?",
                (deadline_id,),
            )
        else:
            cursor = await self._conn.execute(
                "SELECT * FROM deadlines WHERE id = ? AND user_id = ?",
                (deadline_id, user_id),
            )
        row = await cursor.fetchone()
        return _row_to_deadline(row) if row else None

    async def list_by_user(
        self, user_id: int, status: str | None = "active"
    ) -> list[Deadline]:
        """Вернуть список дедлайнов пользователя, отсортированный по сроку."""
        if status is None:
            cursor = await self._conn.execute(
                "SELECT * FROM deadlines WHERE user_id = ? ORDER BY due_date ASC, id ASC",
                (user_id,),
            )
        else:
            cursor = await self._conn.execute(
                """
                SELECT * FROM deadlines
                WHERE user_id = ? AND status = ?
                ORDER BY due_date ASC, id ASC
                """,
                (user_id, status),
            )
        rows = await cursor.fetchall()
        return [_row_to_deadline(row) for row in rows]

    async def update(
        self,
        deadline_id: int,
        user_id: int,
        *,
        title: str | None = None,
        due_date: datetime | None = None,
        hours: float | None = _UNSET,
        weight: float | None = _UNSET,
    ) -> Deadline | None:
        """Обновить параметры существующего дедлайна пользователя."""
        fields: list[str] = []
        values: list[Any] = []

        if title is not None:
            fields.append("title = ?")
            values.append(title)
        if due_date is not None:
            fields.append("due_date = ?")
            values.append(due_date.isoformat(sep=" ", timespec="seconds"))
        if hours is not _UNSET:
            fields.append("hours = ?")
            values.append(hours)
        if weight is not _UNSET:
            fields.append("weight = ?")
            values.append(weight)

        if not fields:
            return await self.get_by_id(deadline_id, user_id=user_id)

        values.extend([deadline_id, user_id])
        cursor = await self._conn.execute(
            f"UPDATE deadlines SET {', '.join(fields)} WHERE id = ? AND user_id = ?",
            values,
        )
        await self._conn.commit()
        if cursor.rowcount == 0:
            return None
        return await self.get_by_id(deadline_id, user_id=user_id)

    async def delete(self, deadline_id: int, user_id: int) -> bool:
        """Удалить дедлайн пользователя. Возвращает True, если запись удалена."""
        cursor = await self._conn.execute(
            "DELETE FROM deadlines WHERE id = ? AND user_id = ?",
            (deadline_id, user_id),
        )
        await self._conn.commit()
        return cursor.rowcount > 0

    async def mark_done(
        self,
        deadline_id: int,
        user_id: int,
        completed_at: datetime | None = None,
    ) -> Deadline | None:
        """Отметить дедлайн выполненным и отменить ожидающие напоминания."""
        done_ts = (completed_at or datetime.now()).isoformat(
            sep=" ", timespec="seconds"
        )
        cursor = await self._conn.execute(
            """
            UPDATE deadlines
            SET status = 'completed', completed_at = ?
            WHERE id = ? AND user_id = ? AND status = 'active'
            """,
            (done_ts, deadline_id, user_id),
        )
        if cursor.rowcount == 0:
            await self._conn.rollback()
            return None

        await self._conn.execute(
            """
            UPDATE notifications
            SET status = 'cancelled'
            WHERE deadline_id = ? AND status = 'pending'
            """,
            (deadline_id,),
        )
        await self._conn.commit()
        return await self.get_by_id(deadline_id, user_id=user_id)
