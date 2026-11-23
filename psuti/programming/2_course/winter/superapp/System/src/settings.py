import os
from re import M

from PyQt5.QtCore import Qt

# --- Пути к приложению ---
SRC_DIR = os.path.dirname(os.path.abspath(__file__))
APP_ROOT = os.path.dirname(SRC_DIR)
MODULES_DIR = os.path.join(SRC_DIR, "modules")

# --- Файлы модулей ---
TERMINAL_SCRIPT = os.path.join(MODULES_DIR, "terminal.py")
MONITORING_SCRIPT = os.path.join(MODULES_DIR, "monitoring.py")
POPUP_SCRIPT = os.path.join(SRC_DIR, "popup.py")
FILEMANAGER_SCRIPT = os.path.join(MODULES_DIR, "filemanager.py")


# --- Среда «Суперапп» (корневая папка-среда) ---
SUPERAPP_ROOT = os.path.dirname(os.path.abspath(APP_ROOT))

# --- Защищённые папки ---
SYSTEM_FOLDER = "System"
TRASH_FOLDER = "Корзина"
PROTECTED_NAMES = frozenset({SYSTEM_FOLDER})

TRASH_PATH = os.path.join(SUPERAPP_ROOT, TRASH_FOLDER)
# --------------- Текст сообщений ---------------
MSG_SYSTEM_PROTECTED = (
    "Папка «{name}» защищена: её нельзя открывать, удалять,\n"
    "переименовывать или перемещать."
)
MSG_OPEN_ERROR = "Не удалось открыть «{name}»:\n{err}"
MSG_NO_SUCH_PATH = "Путь не существует: {path}"
MSG_NOT_A_DIR = "Это не папка: {path}"
MSG_EXISTS = "«{name}» уже существует в этой папке."
MSG_BAD_NAME = "Недопустимое имя: «{name}»"
MSG_PROTECTED_NAME = "Имя «{name}» зарезервировано системой.\nВыберите другое имя."
MSG_CREATE_FAIL = "Не удалось создать «{name}»:\n{err}"
MSG_RENAME_FAIL = "Не удалось переименовать «{name}»:\n{err}"
MSG_DELETE_FAIL = "Не удалось удалить «{name}»:\n{err}"
MSG_TRASH_FAIL = "Не удалось переместить в корзину «{name}»:\n{err}"
MSG_NO_SELECTION = "Сначала выберите элемент в списке."
MSG_DELETE_CONFIRM = "Удалить «{name}» безвозвратно?"
MSG_PASTE_FAIL = "Не удалось вставить «{name}»:\n{err}"

MSG_DND_DROP_SYSTEM = "Папка «System» защищена:\nпомещать объекты внутрь неё нельзя."
MSG_DND_MOVE_FAIL = "Не удалось переместить «{name}»:\n{err}"

# --- Съёмные носители ---
MSG_NO_REMOVABLE = (
    "Съёмные носители не обнаружены.\n"
    "Подключите носитель (USB-флеш-накопитель, CD/DVD)\n"
    "и повторите попытку."
)

MSG_BAD_DIR = "cd: нет такого каталога: {path}\n"
MSG_CD_NOTDIR = "cd: {path} не является каталогом\n"
MSG_EXIT = "exit\n"

MSG_NO_REPORT = "Нет процессов для сохранения: мониторинг ещё не запущен."
MSG_REPORT_SAVED = "Отчёт сохранён:\n{path}\nПроцессов: {n}"
MSG_REPORT_FAIL = "Не удалось сохранить отчёт:\n{err}"
MSG_LOG_SAVED = "Лог-файл сохранён:\n{path}"
MSG_LOG_FAIL = "Не удалось сохранить лог:\n{err}"
MSG_GPU_UNAVAIL = "Не удалось получить информацию о видеокарте."
MSG_POPUP_FAIL = "Не удалось открыть всплывающее окно:\n{err}"

# --------------- Текста ---------------
BANNER = "Суперапп — встроенный терминал Linux. Введите «help» или «?» для справки.\n"
HELP_TEXT = """Доступные команды:

  Встроенные:
    cd [ПУТЬ]        сменить каталог (по умолчанию — корень «Суперапп»)
    pwd              вывести текущий каталог
    ls [ПУТЬ]        список файлов (через shell)
    clear            очистить экран (Ctrl+L)
    history          история команд текущей сессии
    echo ТЕКСТ       вывести текст
    help, ?          эта справка
    exit, quit       закрыть терминал

  Внешние команды выполняются через «bash -c» (напр.: ps aux, top, date, whoami).

  Горячие клавиши:
    Ctrl+C  прервать команду
    Ctrl+L  очистить экран
    Ctrl+D  конец ввода (EOF) — закрыть терминал на пустой строке
    ↑ / ↓   навигация по истории команд
    Tab     (заглушка автодополнения)
"""

ABOUT_TEXT_FILEMANAGER = (
    "Файловый менеджер «Суперапп».\n"
    "Курсовая работа по ОСиО.\n"
    "Язык: Python + PyQt5.\n"
    "Разработчик: Ипатов Даниил Артемович, ИВТ-52зу"
)

ABOUT_TEXT_MONITORING = (
    "Мониторинг процессов «Суперапп».\n"
    "Вариант 5: отслеживаются все процессы ОС, кроме запущенных из приложения.\n"
    "IPC всплывающих окон — именованные каналы (FIFO).\n"
    "Доп. функционал: информация о видеокарте (п.4, item 5).\n"
    "Язык: Python + PyQt5.\n"
    "Разработчик: Ипатов Даниил Артемович, ИВТ-52зу"
)

REPORT_HEADER = (
    "Отчёт о процессах, запущенных во время работы «Суперапп»\n"
    "Сгенерирован: {ts}\n"
    "Всего процессов: {n}\n"
    "----------------------------------------\n"
)

REPORT_LINE = "{name:30}  {start}\n"


# ----------------- Файловый менеджер -----------------
FILEMANAGER_TITLE = "Суперапп"
FILEMANAGER_SIZE = (800, 600)
FILEMANAGER_FOLDER_ICON_URL = os.path.join(MODULES_DIR, "assets", "folder-icon.png")
FILEMANAGER_FILE_ICON_URL = os.path.join(MODULES_DIR, "assets", "file-icon.png")
FILEMANAGER_ICON_SIZE = (64, 64)
FILEMANAGER_GRID_SIZE = (150, 150)

FILEMANAGER_MENU = ["Файл", "Правка", "Вид", "Переход", "Терминал", "Справка"]

FILEMANAGER_ROLE_PATH = Qt.UserRole + 1
FILEMANAGER_ROLE_KIND = Qt.UserRole + 2  # 'dir' | 'file'
FILEMANAGER_ROLE_PROTECTED = Qt.UserRole + 3


# ----------------- Терминал -----------------
TERMINAL_TITLE = "Терминал Суперапп"
TERMINAL_SIZE = (720, 440)

TERMINAL_FONT_FAMILY = "Monospace"
TERMINAL_FONT_SIZE = 11

TERMINAL_COL_BG = "#0c0c0c"
TERMINAL_COL_FG = "#e6e6e6"
TERMINAL_COL_PROMPT = "#7CFC00"  # зелёный — приглашение
TERMINAL_COL_STDOUT = TERMINAL_COL_FG
TERMINAL_COL_STDERR = "#FF5555"  # красный
TERMINAL_COL_INFO = "#56B4E9"  # голубой
TERMINAL_COL_HELP = "#F0E442"  # жёлтый

TERMINAL_PROMPT_USER = "user"
TERMINAL_PROMPT_HOST = "superapp"
TERMINAL_PROMPT_TEMPLATE = "{user}@{host}:{cwd}$ "

TERMINAL_BUILTIN_COMMANDS = (
    "cd",
    "pwd",
    "clear",
    "help",
    "?",
    "history",
    "echo",
    "exit",
    "quit",
)

# ----------------- Мониторинг -----------------
MONITORING_TITLE = "Мониторинг процессов суперапп"
MONITORING_SIZE = (860, 520)

MONITORING_REFRESH_MS = 2000

MONITORING_COLUMNS = ["PID", "Имя", "Пользователь", "Время старта", "Состояние"]

MONITORING_PROC_ROOT = "/proc"
MONITORING_CLK_TCK = os.sysconf(os.sysconf_names["SC_CLK_TCK"])

MONITORING_APP_SCRIPT_NAMES = (
    "filemanager.py",
    "terminal.py",
    "popup.py",
    "monitoring.py",
    "app.py",
    "main.py",
)
