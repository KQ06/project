import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("src.bot.main")


def create_dispatcher() -> Dispatcher:
    """Создание и базовая настройка диспетчера."""
    dp = Dispatcher()

    # Подключение роутеров хендлеров при наличии
    try:
        from src.bot.handlers import add  # type: ignore[import-not-found]

        dp.include_router(add.router)
    except (ImportError, AttributeError):
        pass

    return dp


async def main(bot: Bot | None = None, dp: Dispatcher | None = None) -> None:
    """Точка входа запуска бота."""
    load_dotenv()
    logger.info("Bot started")

    token = os.getenv("BOT_TOKEN")
    if not token and bot is None:
        logger.warning(
            "BOT_TOKEN не задан в переменных окружения или .env. "
            "Укажите BOT_TOKEN для подключения к Telegram API."
        )
        return

    if bot is None:
        bot = Bot(token=token)  # type: ignore[arg-type]

    if dp is None:
        dp = create_dispatcher()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
