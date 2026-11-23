#pragma once
#include <QString>
#include <QStringList>
#include <QSize>
namespace cfg {
inline const QString MSG_SYSTEM_PROTECTED = QString::fromUtf8(R"SUPERAPP(Папка «{name}» защищена: её нельзя открывать, удалять,
переименовывать или перемещать.)SUPERAPP");
inline const QString MSG_OPEN_ERROR = QString::fromUtf8(R"SUPERAPP(Не удалось открыть «{name}»:
{err})SUPERAPP");
inline const QString MSG_NO_SUCH_PATH = QString::fromUtf8(R"SUPERAPP(Путь не существует: {path})SUPERAPP");
inline const QString MSG_NOT_A_DIR = QString::fromUtf8(R"SUPERAPP(Это не папка: {path})SUPERAPP");
inline const QString MSG_EXISTS = QString::fromUtf8(R"SUPERAPP(«{name}» уже существует в этой папке.)SUPERAPP");
inline const QString MSG_BAD_NAME = QString::fromUtf8(R"SUPERAPP(Недопустимое имя: «{name}»)SUPERAPP");
inline const QString MSG_PROTECTED_NAME = QString::fromUtf8(R"SUPERAPP(Имя «{name}» зарезервировано системой.
Выберите другое имя.)SUPERAPP");
inline const QString MSG_CREATE_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось создать «{name}»:
{err})SUPERAPP");
inline const QString MSG_RENAME_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось переименовать «{name}»:
{err})SUPERAPP");
inline const QString MSG_DELETE_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось удалить «{name}»:
{err})SUPERAPP");
inline const QString MSG_TRASH_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось переместить в корзину «{name}»:
{err})SUPERAPP");
inline const QString MSG_NO_SELECTION = QString::fromUtf8(R"SUPERAPP(Сначала выберите элемент в списке.)SUPERAPP");
inline const QString MSG_DELETE_CONFIRM = QString::fromUtf8(R"SUPERAPP(Удалить «{name}» безвозвратно?)SUPERAPP");
inline const QString MSG_PASTE_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось вставить «{name}»:
{err})SUPERAPP");
inline const QString MSG_DND_DROP_SYSTEM = QString::fromUtf8(R"SUPERAPP(Папка «System» защищена:
помещать объекты внутрь неё нельзя.)SUPERAPP");
inline const QString MSG_DND_MOVE_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось переместить «{name}»:
{err})SUPERAPP");
inline const QString MSG_NO_REMOVABLE = QString::fromUtf8(R"SUPERAPP(Съёмные носители не обнаружены.
Подключите носитель (USB-флеш-накопитель, CD/DVD)
и повторите попытку.)SUPERAPP");
inline const QString MSG_BAD_DIR = QString::fromUtf8(R"SUPERAPP(cd: нет такого каталога: {path}
)SUPERAPP");
inline const QString MSG_CD_NOTDIR = QString::fromUtf8(R"SUPERAPP(cd: {path} не является каталогом
)SUPERAPP");
inline const QString MSG_EXIT = QString::fromUtf8(R"SUPERAPP(exit
)SUPERAPP");
inline const QString MSG_T_NOARGS = QString::fromUtf8(R"SUPERAPP({cmd}: не указан операнд
)SUPERAPP");
inline const QString MSG_T_TWOARGS = QString::fromUtf8(R"SUPERAPP({cmd}: нужны два аргумента (источник и назначение)
)SUPERAPP");
inline const QString MSG_T_NOENT = QString::fromUtf8(R"SUPERAPP({cmd}: {path}: нет такого файла или каталога
)SUPERAPP");
inline const QString MSG_T_EXISTS = QString::fromUtf8(R"SUPERAPP({cmd}: {path}: уже существует
)SUPERAPP");
inline const QString MSG_T_ISDIR = QString::fromUtf8(R"SUPERAPP({cmd}: {path}: это каталог
)SUPERAPP");
inline const QString MSG_T_DIRNONEMPTY = QString::fromUtf8(R"SUPERAPP({cmd}: {path}: каталог не пуст
)SUPERAPP");
inline const QString MSG_T_CANTDEL = QString::fromUtf8(R"SUPERAPP({cmd}: {path}: не удалось удалить: {err}
)SUPERAPP");
inline const QString MSG_T_CANTCREATE = QString::fromUtf8(R"SUPERAPP({cmd}: не удалось создать {path}: {err}
)SUPERAPP");
inline const QString MSG_T_CANTCOPY = QString::fromUtf8(R"SUPERAPP({cmd}: не удалось скопировать {src} -> {dst}: {err}
)SUPERAPP");
inline const QString MSG_T_CANTMOVE = QString::fromUtf8(R"SUPERAPP({cmd}: не удалось переместить {src} -> {dst}: {err}
)SUPERAPP");
inline const QString MSG_T_SYSCALL = QString::fromUtf8(R"SUPERAPP({cmd}: ошибка системного вызова: {err}
)SUPERAPP");
inline const QString MSG_T_BADPID = QString::fromUtf8(R"SUPERAPP(kill: {pid}: неверный идентификатор процесса
)SUPERAPP");
inline const QString MSG_T_NOPERM = QString::fromUtf8(R"SUPERAPP(kill: {pid}: операция не разрешена
)SUPERAPP");
inline const QString MSG_T_KILLED = QString::fromUtf8(R"SUPERAPP(kill: сигнал {sig} отправлен процессу {pid}
)SUPERAPP");
inline const QString MSG_T_KILLED_ESRCH = QString::fromUtf8(R"SUPERAPP(kill: {pid}: процесс не существует
)SUPERAPP");
inline const QString MSG_T_PS_HDR = QString::fromUtf8(R"SUPERAPP({pid:>7}  {user:<12}  {state:<4}  {start}  {name}
)SUPERAPP");
inline const QString MSG_T_PS_EMPTY = QString::fromUtf8(R"SUPERAPP((процессов не найдено)
)SUPERAPP");
inline const QString MSG_T_NOVENTRY = QString::fromUtf8(R"SUPERAPP({name}: нет данных ({err})
)SUPERAPP");
inline const QString MSG_JOURNAL_SAVED = QString::fromUtf8(R"SUPERAPP(Журнал файлового менеджера сохранён:
{path}
Записей: {n})SUPERAPP");
inline const QString MSG_JOURNAL_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось сохранить журнал:
{err})SUPERAPP");
inline const QString MSG_NO_REPORT = QString::fromUtf8(R"SUPERAPP(Нет процессов для сохранения: мониторинг ещё не запущен.)SUPERAPP");
inline const QString MSG_REPORT_SAVED = QString::fromUtf8(R"SUPERAPP(Отчёт сохранён:
{path}
Процессов: {n})SUPERAPP");
inline const QString MSG_REPORT_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось сохранить отчёт:
{err})SUPERAPP");
inline const QString MSG_LOG_SAVED = QString::fromUtf8(R"SUPERAPP(Лог-файл сохранён:
{path})SUPERAPP");
inline const QString MSG_LOG_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось сохранить лог:
{err})SUPERAPP");
inline const QString MSG_HOSTNAME_UNAVAIL = QString::fromUtf8(R"SUPERAPP(Не удалось получить имя компьютера.)SUPERAPP");
inline const QString MSG_POPUP_FAIL = QString::fromUtf8(R"SUPERAPP(Не удалось открыть всплывающее окно:
{err})SUPERAPP");
inline const QString BANNER = QString::fromUtf8(R"SUPERAPP(Суперапп — встроенный терминал Linux. Введите «help» или «?» для справки.
)SUPERAPP");
inline const QString HELP_TEXT = QString::fromUtf8(R"SUPERAPP(Доступные команды:

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
)SUPERAPP");
inline const QString ABOUT_TEXT_FILEMANAGER = QString::fromUtf8(R"SUPERAPP(Файловый менеджер «Суперапп».
Курсовая работа по ОСиО.
Язык: Python + PyQt5.
Разработчик: Грекова Екатерина, ИВТ-52зу)SUPERAPP");
inline const QString ABOUT_TEXT_MONITORING = QString::fromUtf8(R"SUPERAPP(Мониторинг процессов «Суперапп».
Вариант 1: отслеживаются все процессы ОС, кроме запущенных из приложения.
IPC всплывающих окон — сокеты (TCP, модель клиент/сервер).
Доп. функционал: имя компьютера (п.4, item 1).
Язык: Python + PyQt5.
Разработчик: Грекова Екатерина, ИВТ-52зу)SUPERAPP");
inline const QString REPORT_HEADER = QString::fromUtf8(R"SUPERAPP(Отчёт о процессах, запущенных во время работы «Суперапп»
Сгенерирован: {ts}
Всего процессов: {n}
----------------------------------------
)SUPERAPP");
inline const QString REPORT_LINE = QString::fromUtf8(R"SUPERAPP({name:30}  {start}
)SUPERAPP");
inline const QString FILEMANAGER_TITLE = QString::fromUtf8(R"SUPERAPP(Суперапп)SUPERAPP");
inline const QString TERMINAL_TITLE = QString::fromUtf8(R"SUPERAPP(Терминал Суперапп)SUPERAPP");
inline const QString TERMINAL_COL_BG = QString::fromUtf8(R"SUPERAPP(#0c0c0c)SUPERAPP");
inline const QString TERMINAL_COL_FG = QString::fromUtf8(R"SUPERAPP(#e6e6e6)SUPERAPP");
inline const QString TERMINAL_COL_PROMPT = QString::fromUtf8(R"SUPERAPP(#7CFC00)SUPERAPP");
inline const QString TERMINAL_COL_STDERR = QString::fromUtf8(R"SUPERAPP(#FF5555)SUPERAPP");
inline const QString TERMINAL_COL_INFO = QString::fromUtf8(R"SUPERAPP(#56B4E9)SUPERAPP");
inline const QString TERMINAL_COL_HELP = QString::fromUtf8(R"SUPERAPP(#F0E442)SUPERAPP");
inline const QString TERMINAL_PROMPT_USER = QString::fromUtf8(R"SUPERAPP(user)SUPERAPP");
inline const QString TERMINAL_PROMPT_HOST = QString::fromUtf8(R"SUPERAPP(superapp)SUPERAPP");
inline const QString TERMINAL_PROMPT_TEMPLATE = QString::fromUtf8(R"SUPERAPP({user}@{host}:{cwd}$ )SUPERAPP");
inline const QString MONITORING_TITLE = QString::fromUtf8(R"SUPERAPP(Мониторинг процессов суперапп)SUPERAPP");
inline const QString SYSTEM_FOLDER = QString::fromUtf8("System");
inline const QString DOCUMENTS_FOLDER = QString::fromUtf8("Документы");
inline const QString DOWNLOADS_FOLDER = QString::fromUtf8("Загрузки");
inline const QString PICTURES_FOLDER = QString::fromUtf8("Изображения");
inline const QString VIDEOS_FOLDER = QString::fromUtf8("Видео");
inline const QString PROJECTS_FOLDER = QString::fromUtf8("Проекты");
inline const QString TRASH_FOLDER = QString::fromUtf8("Корзина");
inline const QString POPUP_HOST = "127.0.0.1";
inline const QSize FILEMANAGER_SIZE{800,600}, TERMINAL_SIZE{720,440}, MONITORING_SIZE{860,520};
inline const QSize FILEMANAGER_ICON_SIZE{64,64}, FILEMANAGER_GRID_SIZE{150,150};
inline constexpr int MONITORING_REFRESH_MS = 2000;
inline constexpr int FILEMANAGER_ROLE_PATH = 257, FILEMANAGER_ROLE_KIND = 258, FILEMANAGER_ROLE_PROTECTED = 259;
QString sourceRoot(); QString appRoot(); QString superappRoot(); QString assetsDir();
QString trashPath(); QString journalPath(); QString siblingExecutable(const QString &name);
QString format(QString pattern, const QString &key, const QString &value);
}
