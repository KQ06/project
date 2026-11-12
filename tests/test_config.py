from pathlib import Path
import pytest
from src.bot.config import ConfigError, Settings, load_settings


def test_load_settings_missing_token(monkeypatch):
    monkeypatch.delenv("BOT_TOKEN", raising=False)
    with pytest.raises(ConfigError) as exc:
        load_settings()
    assert "BOT_TOKEN обязательна" in str(exc.value)


def test_load_settings_success(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "123456:ABC-DEF")
    monkeypatch.setenv("DB_PATH", "data/custom.db")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("ADMIN_IDS", "111,222, 333")

    s = load_settings()
    assert s.bot_token == "123456:ABC-DEF"
    assert s.db_path == Path("data/custom.db")
    assert s.log_level == "DEBUG"
    assert s.admin_ids == (111, 222, 333)


def test_load_settings_default_values(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "test_token")
    monkeypatch.delenv("DB_PATH", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("ADMIN_IDS", raising=False)

    s = load_settings()
    assert s.db_path == Path("data/deadlinebot.db")
    assert s.log_level == "INFO"
    assert s.admin_ids == ()
