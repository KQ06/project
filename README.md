# DeadlineBot - Telegram-бот для контроля учебных дедлайнов и учебной нагрузки

## Функции
- Ввод дедлайнов командами и через диалоговые кнопки.
- Автоматические напоминания за 7, 3 и 1 день до срока.
- Расчёт приоритета задач по формуле: срок, объём, вес в оценке.
- Недельная статистика выполнения (процент закрытых задач).
- Групповой режим: общий календарь дедлайнов для студенческой группы.
- Экспорт расписания в формат .ics.

---

## Документация
Wiki проекта: [перейти в Wiki](https://github.com/KQ06/project/wiki)

Страницы:
- [Home](https://github.com/KQ06/project/wiki/Home) — титульная страница и навигация
- [Backlog](https://github.com/KQ06/project/wiki/Backlog) — бэклог и приоритизация MoSCoW
- [Estimation](https://github.com/KQ06/project/wiki/Estimation) — оценка задач (Planning Poker, PERT), расписание и критический путь
- [Development](https://github.com/KQ06/project/wiki/Development) — процессы разработки, роли и доска
- [Requirements](https://github.com/KQ06/project/wiki/Requirements) — функциональные требования и use cases

---

## Что умеет продукт сейчас

Статус: реализован и откалиброван базовый рабочий инкремент MVP:
- **B-01 (WBS 1.1.1):** Каркас приложения на `aiogram 3`, точка входа `src/bot/main.py`, диспетчер и жизненный цикл.
- **B-02 (WBS 1.1.2):** Конфигурация через `.env` и валидация настроек (`src/bot/config.py`).
- **B-03 (WBS 1.1.3):** Команды `/start` (приветствие и регистрация) и `/help` (справочник команд) в `src/bot/handlers/base.py`.
- **B-06 (WBS 1.3.1):** Команда `/add` с гибким парсингом даты, времени, часов и веса в `src/bot/parsing.py` и `src/bot/handlers/add.py`.
- **Автотесты:** 21 модульный тест в каталоге `tests/` (`test_main.py`, `test_config.py`, `test_base.py`, `test_parsing.py`).

---

## Установка и запуск

1. Склонировать репозиторий и перейти в директорию:
```bash
git clone https://github.com/KQ06/project.git
cd project
```

2. Установить зависимости:
```bash
pip install -r requirements.txt
```

3. Настроить переменные окружения:
```bash
cp .env.example .env
# Укажите ваш BOT_TOKEN в файле .env
```

4. Запустить бота:
```bash
python -m src.bot.main
```

5. Запустить тесты:
```bash
python -m pytest
```

---

## Definition of Done

Задача считается готовой, когда:
1. Код слит в `main` через Pull Request и получил ревью минимум одного участника;
2. Автотесты проходят (`python -m pytest`);
3. Бот запускается локально без ошибок;
4. Секреты не попали в репозиторий;
5. README и Wiki обновлены;
6. Задача закрыта, статус на доске — Done.

Подробности процесса: [Development](https://github.com/KQ06/project/wiki/Development), команда: [Team](https://github.com/KQ06/project/wiki/Team), оценки: [Estimation](https://github.com/KQ06/project/wiki/Estimation).
