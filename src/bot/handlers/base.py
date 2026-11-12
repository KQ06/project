from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()

HELP_TEXT = (
    "📋 <b>Команды DeadlineBot:</b>\n\n"
    "<b>Основные:</b>\n"
    "• /start — начать работу с ботом\n"
    "• /help — список всех доступных команд\n"
    "• /add &lt;название&gt; | &lt;дата&gt; | [часы] | [вес] — добавить дедлайн\n"
    "• /list — список активных задач\n"
    "• /done &lt;id&gt; — отметить дедлайн выполненным\n"
    "• /edit &lt;id&gt; — изменить параметры дедлайна\n"
    "• /delete &lt;id&gt; — удалить дедлайн\n\n"
    "<b>Планирование и аналитика:</b>\n"
    "• /top — задачи, отсортированные по приоритету\n"
    "• /stats — недельная статистика выполнения задач\n"
    "• /timezone — настройка часового пояса и времени напоминаний\n"
    "• /export — экспорт расписания дедлайнов в формат .ics (календарь)\n\n"
    "<b>Групповой режим:</b>\n"
    "• /group_create — создать учебную группу\n"
    "• /join &lt;код&gt; — присоединиться к группе по коду приглашения\n"
    "• /group — общие дедлайны группы"
)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user_name = message.from_user.first_name if message.from_user else "Студент"
    welcome_text = (
        f"👋 Привет, <b>{user_name}</b>!\n\n"
        "Я <b>DeadlineBot</b> — твой персональный помощник по контролю учебных дедлайнов.\n\n"
        "Я помогу:\n"
        "✅ Вести учёт лабораторных, курсовых и домашних заданий\n"
        "⏰ Напоминать о приближающихся сроках за 7, 3 и 1 день\n"
        "📊 Приоритизировать задачи, чтобы сдавать всё вовремя\n\n"
        "Чтобы добавить первый дедлайн, используй команду:\n"
        "<code>/add Лабораторная 5 | 20.11.2026 23:59 | 6 | 10</code>\n\n"
        "Полный список команд: /help"
    )
    await message.answer(welcome_text, parse_mode="HTML")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, parse_mode="HTML")
