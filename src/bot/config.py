import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv


class ConfigError(ValueError):
    """Ошибка конфигурации приложения."""


@dataclass(frozen=True)
class Settings:
    bot_token: str
    db_path: Path
    log_level: str
    admin_ids: tuple[int, ...]


def load_settings(env_file: str | Path | None = None) -> Settings:
    """Загрузка и валидация конфигурации из переменных окружения и .env."""
    if env_file:
        load_dotenv(dotenv_path=env_file)
    else:
        load_dotenv()

    token = os.getenv("BOT_TOKEN", "").strip()
    if not token:
        raise ConfigError("Переменная окружения BOT_TOKEN обязательна для запуска бота")

    db_path_raw = os.getenv("DB_PATH", "data/deadlinebot.db").strip()
    db_path = Path(db_path_raw)

    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper()
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    if log_level not in valid_levels:
        log_level = "INFO"

    admin_ids_raw = os.getenv("ADMIN_IDS", "").strip()
    admin_ids: list[int] = []
    if admin_ids_raw:
        for part in admin_ids_raw.split(","):
            part = part.strip()
            if part.isdigit():
                admin_ids.append(int(part))

    return Settings(
        bot_token=token,
        db_path=db_path,
        log_level=log_level,
        admin_ids=tuple(admin_ids),
    )
