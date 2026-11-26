import sqlite3
import pytest

from src.bot.db.database import get_schema_sql, init_db_sync


def test_schema_creates_required_tables():
    conn = init_db_sync(":memory:")
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        table_names = {row[0] for row in rows}
        assert {"users", "deadlines", "notifications"}.issubset(table_names)
    finally:
        conn.close()


def test_schema_creates_indexes_on_user_id_and_due_date():
    conn = init_db_sync(":memory:")
    try:
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'index'"
        ).fetchall()
        index_names = {row[0] for row in rows}
        assert "idx_deadlines_user_id" in index_names
        assert "idx_deadlines_due_date" in index_names
        assert "idx_notifications_deadline_id" in index_names
    finally:
        conn.close()


def test_schema_enforces_foreign_keys():
    conn = init_db_sync(":memory:")
    try:
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO deadlines (user_id, title, due_date) VALUES (?, ?, ?)",
                (999999, "Лаба 5", "2026-12-01 23:59:00"),
            )

        conn.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (101, "kq06", "Андрей"),
        )
        conn.execute(
            "INSERT INTO deadlines (id, user_id, title, due_date) VALUES (?, ?, ?, ?)",
            (1, 101, "Лаба 5", "2026-12-01 23:59:00"),
        )
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute(
                "INSERT INTO notifications (deadline_id, offset_days, planned_at) VALUES (?, ?, ?)",
                (888, 3, "2026-11-28 09:00:00"),
            )
    finally:
        conn.close()


def test_init_db_sync_file_path_creates_parent_dir(tmp_path):
    db_file = tmp_path / "nested" / "deadlinebot.db"
    conn = init_db_sync(db_file)
    try:
        assert db_file.exists()
        assert "CREATE TABLE IF NOT EXISTS deadlines" in get_schema_sql()
    finally:
        conn.close()
