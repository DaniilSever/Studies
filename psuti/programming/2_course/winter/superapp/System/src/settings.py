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

# --- Папки ---
SYSTEM_FOLDER = "System"
DOCUMENTS_FOLDER = "Документы"
DOWNLOADS_FOLDER = "Загрузки"
PICTURES_FOLDER = "Изображения"
VIDEOS_FOLDER = "Видео"
PROJECTS_FOLDER = "Проекты"
TRASH_FOLDER = "Корзина"

# --- Защищенная папка ---
PROTECTED_NAMES = frozenset({SYSTEM_FOLDER})


DOCUMENTS_PATH = os.path.join(SUPERAPP_ROOT, DOCUMENTS_FOLDER)
DOWNLOADS_PATH = os.path.join(SUPERAPP_ROOT, DOWNLOADS_FOLDER)
PICTURES_PATH = os.path.join(SUPERAPP_ROOT, PICTURES_FOLDER)
VIDEOS_PATH = os.path.join(SUPERAPP_ROOT, VIDEOS_FOLDER)
PROJECTS_PATH = os.path.join(SUPERAPP_ROOT, PROJECTS_FOLDER)
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

# --- Терминал: сообщения встроенных команд (сисколлы) ---
MSG_T_NOARGS = "{cmd}: не указан операнд\n"
MSG_T_TWOARGS = "{cmd}: нужны два аргумента (источник и назначение)\n"
MSG_T_NOENT = "{cmd}: {path}: нет такого файла или каталога\n"
MSG_T_EXISTS = "{cmd}: {path}: уже существует\n"
MSG_T_ISDIR = "{cmd}: {path}: это каталог\n"
MSG_T_DIRNONEMPTY = "{cmd}: {path}: каталог не пуст\n"
MSG_T_CANTDEL = "{cmd}: {path}: не удалось удалить: {err}\n"
MSG_T_CANTCREATE = "{cmd}: не удалось создать {path}: {err}\n"
MSG_T_CANTCOPY = "{cmd}: не удалось скопировать {src} -> {dst}: {err}\n"
MSG_T_CANTMOVE = "{cmd}: не удалось переместить {src} -> {dst}: {err}\n"
MSG_T_SYSCALL = "{cmd}: ошибка системного вызова: {err}\n"
MSG_T_BADPID = "kill: {pid}: неверный идентификатор процесса\n"
MSG_T_NOPERM = "kill: {pid}: операция не разрешена\n"
MSG_T_KILLED = "kill: сигнал {sig} отправлен процессу {pid}\n"
MSG_T_KILLED_ESRCH = "kill: {pid}: процесс не существует\n"
MSG_T_PS_HDR = "{pid:>7}  {user:<12}  {state:<4}  {start}  {name}\n"
MSG_T_PS_EMPTY = "(процессов не найдено)\n"
MSG_T_NOVENTRY = "{name}: нет данных ({err})\n"

# --- Журнал файлового менеджера ---
FM_JOURNAL_NAME = "fm_journal.log"
FM_JOURNAL_PATH = os.path.join(APP_ROOT, FM_JOURNAL_NAME)
MSG_JOURNAL_SAVED = "Журнал файлового менеджера сохранён:\n{path}\nЗаписей: {n}"
MSG_JOURNAL_FAIL = "Не удалось сохранить журнал:\n{err}"

MSG_NO_REPORT = "Нет процессов для сохранения: мониторинг ещё не запущен."
MSG_REPORT_SAVED = "Отчёт сохранён:\n{path}\nПроцессов: {n}"
MSG_REPORT_FAIL = "Не удалось сохранить отчёт:\n{err}"
MSG_LOG_SAVED = "Лог-файл сохранён:\n{path}"
MSG_LOG_FAIL = "Не удалось сохранить лог:\n{err}"
MSG_HOSTNAME_UNAVAIL = "Не удалось получить имя компьютера."
MSG_POPUP_FAIL = "Не удалось открыть всплывающее окно:\n{err}"

# --- IPC всплывающих окон (вар. 1: сокеты) ---
POPUP_HOST = "127.0.0.1"

# --------------- Текста ---------------
BANNER = "Суперапп — встроенный терминал Linux. Введите «help» или «?» для справки.\n"
HELP_TEXT = """Доступные команды:

  Встроенные (реализованы системными вызовами — без shell):
    cd [ПУТЬ]        сменить каталог (по умолчанию — корень «Суперапп»)
    pwd              вывести текущий каталог (getcwd)
    ls [ПУТЬ]        список файлов каталога (listdir/stat)
    mkdir ПУТЬ       создать каталог (mkdir)
    rmdir ПУТЬ       удалить пустой каталог (rmdir)
    cp ИСТ ДСТ       скопировать файл/каталог (read/write, каталог — рекурсивно)
    mv ИСТ ДСТ       переместить/переименовать (rename)
    rm [-r] ПУТЬ     удалить файл или каталог (unlink/rmdir, -r — рекурсивно)
    clear            очистить экран (Ctrl+L)
    history          история команд текущей сессии
    echo ТЕКСТ       вывести текст
    help, ?          эта справка
    exit, quit       закрыть терминал

  Вариант 1 (нечётный): управление процессами + устройства ввода/вывода:
    ps               список процессов ОС (чтение /proc/[pid]/stat)
    kill PID [СИГ]   отправить сигнал процессу (kill)
    lsdev            список блочных/символьных устройств /dev
                     (listdir/stat по /dev)
    mounts           список смонтированных ФС (чтение /proc/mounts)
    ioports          карта портов ввода/вывода (чтение /proc/ioports)

  Внешние команды выполняются через «bash -c» (напр.: top, date, whoami).

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
    "Вариант 1: отслеживаются все процессы ОС, кроме запущенных из приложения.\n"
    "IPC всплывающих окон — сокеты (TCP, модель клиент/сервер).\n"
    "Доп. функционал: имя компьютера (п.4, item 1).\n"
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
    # базовый набор
    "cd",
    "pwd",
    "clear",
    "help",
    "?",
    "history",
    "echo",
    "exit",
    "quit",
    # файловые операции — сисколлы (os.listdir/os.mkdir/os.rename/...)
    "ls",
    "mkdir",
    "rmdir",
    "cp",
    "mv",
    "rm",
    # вариант 1 (нечётный): управление процессами + устройства ввода/вывода
    "ps",
    "kill",
    "lsdev",
    "mounts",
    "ioports",
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
