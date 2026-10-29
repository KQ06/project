from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.bot.parsing import ParseError, parse_add_args

router = Router()

USAGE = (
    "Формат: /add название | дата | часы | вес\n"
    "Пример: /add Лабораторная 4 | 15.11.2026 23:59 | 6 | 10"
)


@router.message(Command("add"))
async def cmd_add(message: Message, command: CommandObject) -> None:
    if not command.args:
        await message.answer(USAGE)
        return
    try:
        data = parse_add_args(command.args)
    except ParseError as exc:
        await message.answer(f"⚠️ {exc}\n\n{USAGE}")
        return


    deadline_id = 1  # временно, пока нет хранилища
    await message.answer(
        f"✅ Дедлайн №{deadline_id} добавлен\n"
        f"{data.title}\nСрок: {data.due:%d.%m.%Y %H:%M}"
    )
