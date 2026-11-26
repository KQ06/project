import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def get_schema_sql() -> str:
    """Прочитать DDL-скрипт инициализации базы данных SQLite."""
    return SCHEMA_PATH.read_text(encoding="utf-8")


def init_db_sync(db_path: str | Path) -> sqlite3.Connection:
    """Создать таблицы и индексы в SQLite и вернуть открытое соединение."""
    path_str = str(db_path)
    if path_str != ":memory:":
        Path(path_str).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path_str)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(get_schema_sql())
    conn.commit()
    return conn
