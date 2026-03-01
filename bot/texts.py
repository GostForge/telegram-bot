"""
Все текстовые сообщения бота GostForge.

Редактируйте строки здесь — обработчики импортируют их автоматически.
Поддерживается HTML-разметка Telegram (ParseMode.HTML).
"""

# ══════════════════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════════════════

START_BUTTON_LOGIN = "🔐 Войти / Зарегистрироваться"

START_WELCOME = (
    "👋 Привет! Я бот <b>GostForge</b>.\n\n"
    "Конвертирую Markdown → DOCX/PDF по ГОСТ.\n\n"
    "<b>Как начать:</b>\n"
    "{link_step}"
    "2. Отправьте <code>/convert</code>, <code>/pdf</code> или <code>/both</code>\n"
    "3. Отправьте <code>.md</code> или <code>.zip</code> файл\n\n"
    "<b>Команды:</b>\n"
    "/convert — конвертировать → DOCX\n"
    "/pdf — конвертировать → PDF\n"
    "/both — конвертировать → DOCX + PDF\n"
    "/status — статус текущей конвертации\n"
    "/link &lt;code&gt; — привязать аккаунт по коду\n"
    "/unlink — отвязать аккаунт"
)

START_LINK_STEP_MINIAPP = (
    "1. Нажмите кнопку ниже — войдите или зарегистрируйтесь, "
    "Telegram привяжется автоматически\n"
)

START_LINK_STEP_FALLBACK = (
    '1. Привяжите аккаунт: <code>/link &lt;code&gt;</code> '
    "(код — в веб-интерфейсе)\n"
)

# ══════════════════════════════════════════════════════════
#  /convert, /pdf, /both
# ══════════════════════════════════════════════════════════

CONVERT_PROMPT = (
    "📎 Отправьте <code>.md</code> или <code>.zip</code> файл (до 20 MB).\n"
    "Формат: <b>{fmt}</b>"
)

CONVERT_BAD_EXT = "⚠️ Отправьте файл <code>.md</code> или <code>.zip</code>."

CONVERT_TOO_BIG = (
    "❗ Файл слишком большой ({size} MB). "
    "Максимум: {limit} MB."
)

CONVERT_DOWNLOADING = "⏳ Скачиваю файл..."
CONVERT_SUBMITTING = "🔄 Отправляю на конвертацию..."

CONVERT_NOT_LINKED = (
    "❌ Аккаунт не привязан.\n"
    "Нажмите /start и авторизуйтесь через кнопку,\n"
    "или используйте /link &lt;code&gt;."
)

CONVERT_ACTIVE_JOB = (
    "⚠️ У вас уже есть активная конвертация.\n"
    "Дождитесь завершения или проверьте /status."
)

CONVERT_ERROR = "❌ Ошибка: {msg}"

CONVERT_EXPECT_FILE = "⚠️ Ожидаю файл <code>.md</code> или <code>.zip</code>. Отправьте документ."

CONVERT_DONE_SENDING = "✅ Готово! Отправляю файлы..."
CONVERT_TIMEOUT = "⏰ Превышено время ожидания. Попробуйте позже."
CONVERT_FAILED = "❌ Конвертация не удалась: {err}"
CONVERT_DELIVERY_FAIL = "❌ Не удалось скачать результат: {err}"

# ── Status labels used during polling ─────────────────────

STATUS_PENDING = "⏳ В очереди"
STATUS_PENDING_POS = "⏳ В очереди (позиция: {pos})"
STATUS_MERGING_MD = "📝 Объединяю Markdown файлы..."
STATUS_CONVERTING_DOCX = "📄 Конвертирую в DOCX..."
STATUS_CONVERTING_PDF = "📑 Конвертирую в PDF..."
STATUS_COMPLETED = "✅ Готово!"
STATUS_FAILED = "❌ Ошибка"
STATUS_UNKNOWN = "🔄 {status}..."

# ══════════════════════════════════════════════════════════
#  /status
# ══════════════════════════════════════════════════════════

STATUS_NO_JOBS = "ℹ️ Нет активных конвертаций. Используйте /convert для запуска."
STATUS_NOT_FOUND = "ℹ️ Конвертация не найдена. Запустите новую: /convert"
STATUS_ERROR = "❌ Ошибка: {msg}"

STATUS_JOB_COMPLETED = "✅ Конвертация завершена!\nФормат: {fmt}\nID: <code>{job_id}</code>"
STATUS_JOB_FAILED = "❌ Конвертация не удалась.\nОшибка: {err}"
STATUS_JOB_PENDING = "⏳ В очереди{pos}\nФормат: {fmt}"
STATUS_JOB_IN_PROGRESS = "🔄 Статус: {status}\nФормат: {fmt}"

# ══════════════════════════════════════════════════════════
#  /link
# ══════════════════════════════════════════════════════════

LINK_USAGE = (
    "Использование: <code>/link 123456</code>\n\n"
    "Получите код в веб-портале: <i>Профиль → Привязка Telegram</i>"
)

LINK_SUCCESS = (
    "✅ Аккаунт <b>{username}</b> успешно привязан!\n\n"
    "Теперь можно конвертировать файлы: /convert"
)

LINK_INVALID_CODE = "❌ Неверный или истёкший код. Получите новый в веб-портале."
LINK_ALREADY_LINKED = "❌ Этот Telegram-аккаунт уже привязан к другому пользователю."
LINK_ERROR = "❌ Ошибка привязки: {msg}"

# ══════════════════════════════════════════════════════════
#  /unlink
# ══════════════════════════════════════════════════════════

UNLINK_INFO = (
    "🔓 Чтобы отвязать Telegram, откройте auth-портал:\n"
    "<i>Профиль → Отвязать Telegram</i>\n\n"
    "После отвязки бот не сможет конвертировать файлы от вашего имени."
)
