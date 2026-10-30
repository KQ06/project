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
- [Home](https://github.com/KQ06/project/wiki/Home)
- [Ideas](https://github.com/KQ06/project/wiki/Ideas)
- [Evaluation](https://github.com/KQ06/project/wiki/Evaluation)
- [Concept](https://github.com/KQ06/project/wiki/Concept)
- [Stakeholders](https://github.com/KQ06/project/wiki/Stakeholders)

## Что умеет продукт сейчас

Статус: реализован базовый каркас бота (задача B-01, WBS 1.1.1).

- Каркас приложения: точка входа `src/bot/main.py` на базе `aiogram 3`.
- При старте инициализируется диспетчер, логируется событие «Bot started».
- Управление зависимостями: `requirements.txt`.
- Автотесты: базовые тесты инициализации и запуска в `tests/test_main.py`.

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

3. (Опционально) Настроить переменные окружения:
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
pytest
```

## Definition of Done

Задача считается готовой, когда:

1. код слит в `main` через Pull Request и получил ревью минимум одного участника;
2. автотесты проходят;
3. бот запускается локально без ошибок;
4. секреты не попали в репозиторий;
5. README и Wiki обновлены;
6. задача закрыта, статус на доске — Done.

Подробности процесса: [Development](https://github.com/KQ06/project/wiki/Development), команда: [Team](https://github.com/KQ06/project/wiki/Team).
