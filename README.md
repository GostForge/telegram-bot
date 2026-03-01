# GostForge Telegram Bot

Telegram-бот на Aiogram 3.x для конвертации Markdown-документов в DOCX/PDF по ГОСТ через внутренний API GostForge.

## Возможности

- `/convert` — конвертация в DOCX, `/pdf` — в PDF, `/both` — оба формата
- Принимает `.md` и `.zip` файлы (до 20 МБ по умолчанию)
- `/link <code>` — привязка Telegram-аккаунта к веб-аккаунту GostForge
- `/status` — проверка статуса последней задачи конвертации
- `/unlink` — инструкция по отвязке аккаунта
- Автопривязка через Telegram Mini App (WebApp)

## Стек

- Python 3.11, aiogram 3.x, httpx, pydantic-settings
- FSM (Finite State Machine) для многошагового процесса конвертации
- Аутентификация внутреннего API (`X-Internal-Api-Key` + `X-Telegram-Chat-Id`)

## Установка и запуск

### Требования

- Запущенный backend GostForge (см. `../infra/docker-compose.yml`)
- Telegram Bot Token от [@BotFather](https://t.me/BotFather)

### Переменные окружения

| Переменная | Обязательна | По умолчанию | Описание |
|---|---|---|---|
| `GOSTFORGE_BOT_TOKEN` | ✅ | — | Токен Telegram-бота |
| `GOSTFORGE_BACKEND_URL` |  | `http://backend:8080` | Базовый URL backend |
| `GOSTFORGE_INTERNAL_API_KEY` |  | `gostforge_internal_dev` | Ключ внутреннего API |
| `GOSTFORGE_MINI_APP_URL` |  | `http://localhost:3001` | URL фронтенда / Mini App |
| `GOSTFORGE_MAX_FILE_SIZE_MB` |  | `20` | Максимальный размер входного файла (МБ) |

### Локальный запуск

```bash
cd telegram
poetry install
GOSTFORGE_BOT_TOKEN=your_token_here \
GOSTFORGE_INTERNAL_API_KEY=gostforge_internal_dev \
poetry run gostforge-bot
```

### Запуск через Docker Compose

```bash
cd infra
# Укажите GOSTFORGE_BOT_TOKEN в .env
docker compose up -d telegram
```

## Команды

| Команда | Описание |
|---|---|
| `/start` | Приветствие + кнопка авторизации через Mini App |
| `/convert` | Конвертация загруженного файла в DOCX |
| `/pdf` | Конвертация загруженного файла в PDF |
| `/both` | Конвертация в DOCX + PDF |
| `/link <code>` | Привязка Telegram-аккаунта по коду из веб-интерфейса |
| `/status` | Статус последней задачи |
| `/unlink` | Инструкция по отвязке аккаунта |

## Структура исходников

```text
telegram/
├── pyproject.toml
└── bot/
    ├── config.py          # pydantic-settings, env-переменные GOSTFORGE_*
    ├── main.py            # Запуск бота, dispatcher, middleware
    ├── client.py          # Async HTTP-клиент для Internal API
    ├── handlers.py        # Агрегатор роутеров (импортирует все модули handlers)
    └── handlers/
        ├── start.py       # /start — приветствие + кнопка Mini App
        ├── link.py        # /link <code> — привязка аккаунта
        ├── convert.py     # /convert, /pdf, /both — FSM загрузки и конвертации
        ├── status.py      # /status — проверка статуса последней задачи
        └── unlink.py      # /unlink — информация по отвязке
```

## Как это работает

```text
Пользователь → /convert → отправляет .md или .zip
  → Бот скачивает файл → POST /internal/convert/quick (Internal API)
  → Backend ставит задачу в очередь → md2gost → Gotenberg → DOCX/PDF в MinIO
  → Бот опрашивает GET /internal/jobs/{id} до статуса COMPLETED
  → Бот отправляет пользователю готовый файл
```

**Автопривязка через Mini App:**
Когда пользователь открывает Mini App из кнопки в `/start`, фронтенд получает токен `initData` от Telegram и отправляет его в `POST /auth/telegram` на backend. Backend автоматически создаёт/находит аккаунт и связывает его с Telegram без ручной команды `/link`.

## Лицензия

Часть проекта GostForge. См. LICENSE в корне соответствующего репозитория.
