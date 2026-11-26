from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.bot.db.repository import DeadlineRepository
from src.bot.parsing import ParseError, parse_add_args

router = Router()

USAGE = (
    "Формат: /add название | дата | часы | вес\n"
    "Пример: /add Лабораторная 4 | 15.11.2026 23:59 | 6 | 10"
)


@router.message(Command("add"))
async def cmd_add(
    message: Message,
    command: CommandObject,
    repo: DeadlineRepository | None = None,
) -> None:
    if not command.args:
        await message.answer(USAGE)
        return
    try:
        data = parse_add_args(command.args)
    except ParseError as exc:
        await message.answer(f"⚠️ {exc}\n\n{USAGE}")
        return

    if repo is not None and message.from_user is not None:
        await repo.ensure_user(
            user_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
        )
        deadline = await repo.create(
            user_id=message.from_user.id,
            title=data.title,
            due_date=data.due,
            hours=data.hours,
            weight=data.weight,
        )
        deadline_id = deadline.id
    else:
        deadline_id = 1

    await message.answer(
        f"✅ Дедлайн №{deadline_id} добавлен\n"
        f"{data.title}\nСрок: {data.due:%d.%m.%Y %H:%M}"
    )
