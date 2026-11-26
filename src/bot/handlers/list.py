import html
import math
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from src.bot.db.repository import Deadline, DeadlineRepository

router = Router()

PAGE_SIZE = 10


def format_remaining(due_date: datetime, now: datetime) -> str:
    """Сформировать человекочитаемое описание оставшегося времени до дедлайна."""
    total_seconds = int((due_date - now).total_seconds())
    if total_seconds <= 0:
        overdue_hours = abs(total_seconds) // 3600
        if overdue_hours >= 24:
            return f"просрочен на {overdue_hours // 24} дн."
        if overdue_hours >= 1:
            return f"просрочен на {overdue_hours} ч"
        return "срок истёк"

    total_hours = total_seconds // 3600
    days, hours = divmod(total_hours, 24)
    if days > 0:
        return f"осталось {days} дн. {hours} ч" if hours else f"осталось {days} дн."
    if hours > 0:
        return f"осталось {hours} ч"
    minutes = max(1, total_seconds // 60)
    return f"осталось {minutes} мин"


def build_list_page(
    deadlines: list[Deadline],
    page: int = 1,
    page_size: int = PAGE_SIZE,
    now: datetime | None = None,
) -> tuple[str, InlineKeyboardMarkup | None]:
    """Сформировать текст списка дедлайнов и клавиатуру пагинации."""
    if not deadlines:
        return (
            "Дедлайнов нет 🎉\n\n"
            "Добавь первый дедлайн командой:\n"
            "<code>/add Лабораторная 5 | 20.12.2026 23:59 | 6 | 10</code>",
            None,
        )

    now = now or datetime.now()
    total_pages = math.ceil(len(deadlines) / page_size)
    current_page = max(1, min(page, total_pages))
    start = (current_page - 1) * page_size
    chunk = deadlines[start : start + page_size]

    lines = [f"📋 <b>Активные дедлайны ({len(deadlines)}):</b>\n"]
    for d in chunk:
        title = html.escape(d.title)
        remaining = format_remaining(d.due_date, now)
        lines.append(
            f"• <b>№{d.id}</b> {title}\n"
            f"  📅 {d.due_date:%d.%m.%Y %H:%M} — <i>{remaining}</i>"
        )

    keyboard: InlineKeyboardMarkup | None = None
    if total_pages > 1:
        lines.append(f"\nСтраница {current_page} из {total_pages}")
        buttons: list[InlineKeyboardButton] = []
        if current_page > 1:
            buttons.append(
                InlineKeyboardButton(
                    text="◀️ Назад",
                    callback_data=f"list_page:{current_page - 1}",
                )
            )
        buttons.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}",
                callback_data="list_page:noop",
            )
        )
        if current_page < total_pages:
            buttons.append(
                InlineKeyboardButton(
                    text="Вперёд ▶️",
                    callback_data=f"list_page:{current_page + 1}",
                )
            )
        keyboard = InlineKeyboardMarkup(inline_keyboard=[buttons])

    return "\n".join(lines), keyboard


@router.message(Command("list"))
async def cmd_list(
    message: Message,
    repo: DeadlineRepository | None = None,
    now: datetime | None = None,
) -> None:
    if repo is None or message.from_user is None:
        text, keyboard = build_list_page([], now=now)
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)
        return

    deadlines = await repo.list_by_user(message.from_user.id, status="active")
    text, keyboard = build_list_page(deadlines, page=1, now=now)
    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data.startswith("list_page:"))
async def cb_list_page(
    callback: CallbackQuery,
    repo: DeadlineRepository | None = None,
    now: datetime | None = None,
) -> None:
    raw = (callback.data or "").split(":", maxsplit=1)[-1]
    if raw == "noop" or not raw.isdigit():
        await callback.answer()
        return

    page = int(raw)
    if repo is None or callback.from_user is None or callback.message is None:
        await callback.answer()
        return

    deadlines = await repo.list_by_user(callback.from_user.id, status="active")
    text, keyboard = build_list_page(deadlines, page=page, now=now)
    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    await callback.answer()
