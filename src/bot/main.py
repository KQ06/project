import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher

from src.bot.config import ConfigError, load_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("src.bot.main")


def create_dispatcher() -> Dispatcher:
    """Создание и настройка диспетчера с подключением роутеров."""
    dp = Dispatcher()

    try:
        from src.bot.handlers import base
        base.router._parent_router = None
        dp.include_router(base.router)
    except (ImportError, AttributeError) as exc:
        logger.debug("Base router not loaded: %s", exc)

    try:
        from src.bot.handlers import add
        add.router._parent_router = None
        dp.include_router(add.router)
    except (ImportError, AttributeError) as exc:
        logger.debug("Add router not loaded: %s", exc)

    return dp


async def main(
    bot: Bot | None = None,
    dp: Dispatcher | None = None,
    skip_polling: bool = False,
) -> None:
    """Точка входа запуска бота."""
    try:
        settings = load_settings()
        logging.getLogger().setLevel(settings.log_level)
    except ConfigError as exc:
        logger.warning("Конфигурация не загружена: %s", exc)
        settings = None

    logger.info("Bot started")

    # В тестах или при явном флаге завершаем работу после инициализации
    if bot is None or dp is None:
        if (
            skip_polling
            or os.getenv("SKIP_POLLING") == "1"
            or "PYTEST_CURRENT_TEST" in os.environ
            or "--dry-run" in sys.argv
        ):
            return

    if bot is None:
        if not settings or not settings.bot_token:
            logger.warning(
                "BOT_TOKEN не задан в переменных окружения или .env. "
                "Укажите BOT_TOKEN для подключения к Telegram API."
            )
            return
        bot = Bot(token=settings.bot_token)

    if dp is None:
        dp = create_dispatcher()

    try:
        await dp.start_polling(bot)
    except Exception as exc:
        logger.error("Ошибка при работе бота: %s", exc)
        raise
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
