from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Protocol, runtime_checkable

# Категории --------------------------------------------------------------------
CAT_FILE = "Файловый менеджер"
CAT_NAV = "Навигация"
CAT_EDIT = "Правка"
CAT_VIEW = "Вид"
CAT_TERM = "Терминал"
CAT_MON = "Мониторинг"
CAT_APP = "Приложение"

# Контексты (строки, без Qt-импортов): UI в app.py переведёт в Qt-контекст -----
CTX_GLOBAL = "global"  # действует во всём приложении
CTX_FILEMANAGER = "filemanager"
CTX_TERMINAL = "terminal"


# Допустимые модификаторы и «базовые» клавиши для валидации --------------------
_MODIFIERS = {"Ctrl", "Shift", "Alt", "Meta"}
_SPECIALS = {
    "Esc",
    "Tab",
    "Backtab",
    "Backspace",
    "Return",
    "Enter",
    "Insert",
    "Delete",
    "Home",
    "End",
    "PageUp",
    "PageDown",
    "Left",
    "Right",
    "Up",
    "Down",
    "F1",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "F10",
    "F11",
    "F12",
    "Space",
    "Pause",
    "Print",
    "CapsLock",
}


@dataclass(frozen=True)
class ShortcutEntry:
    """Одно сочетание клавиш.

    sequence — строка в нотации QKeySequence ("Ctrl+S", "Alt+Left", "F5",
               "Shift+Delete" и т.п.); на «+»-разделённых токенах.
    context  — где сочетание активно (см. CTX_*).
    """

    id: str
    sequence: str
    description: str
    category: str = CAT_APP
    context: str = CTX_GLOBAL

    def __post_init__(self) -> None:
        # нормализуем и валидируем сразу при создании
        norm = normalize_sequence(self.sequence)
        if norm is None:
            raise ValueError(f"Некорректная комбинация: {self.sequence!r}")
        object.__setattr__(self, "sequence", norm)


# ======================================================================
#  Парсинг / валидация / нормализация
# ======================================================================
def _tokenize(sequence: str) -> list[str]:
    return [t.strip() for t in sequence.split("+") if t.strip()]


def normalize_sequence(sequence: str) -> str | None:
    """Привести к каноническому виду "Mod1+Mod2+...+Base" или вернуть None.

    Правила:
      * токены разделяются '+' (с пробелами или без);
      * модификаторы приводятся к заглавной первой букве (Ctrl, Shift, Alt, Meta);
      * спец-клавиши — с заглавной первой буквы (F5, Delete, ft ...);
      * одиночная буква/цифра — в верхнем регистре;
      * модификаторы идут в фиксированном порядке: Ctrl, Shift, Alt, Meta;
      * ровно одна «базовая» клавиша в конце;
      * пустая строка -> None.
    """
    if not sequence or not sequence.strip():
        return None
    tokens = _tokenize(sequence)
    if not tokens:
        return None

    mods: dict[str, bool] = {"Ctrl": False, "Shift": False, "Alt": False, "Meta": False}
    base: str | None = None

    for raw in tokens:
        t = raw.strip()
        if not t:
            return None
        cap = t[:1].upper() + t[1:]
        if cap in _MODIFIERS:
            mods[cap] = True
            continue
        # спец-клавиша
        if cap in _SPECIALS:
            if base is not None:
                return None
            base = cap
            continue
        # буква/цифра
        if len(t) == 1 and (t.isalnum()):
            if base is not None:
                return None
            base = t.upper()
            continue
        return None

    if base is None:
        return None

    parts = [m for m in ("Ctrl", "Shift", "Alt", "Meta") if mods[m]]
    parts.append(base)
    return "+".join(parts)


def is_valid_sequence(sequence: str) -> bool:
    return normalize_sequence(sequence) is not None


# ======================================================================
#  Интерфейс реестра
# ======================================================================
@runtime_checkable
class ShortcutRegistry(Protocol):
    """Источник правды по горячим клавишам для UI."""

    def get_all(self) -> list[ShortcutEntry]: ...
    def get_by_id(self, shortcut_id: str) -> ShortcutEntry | None: ...
    def get_by_category(self, category: str) -> list[ShortcutEntry]: ...
    def get_by_context(self, context: str) -> list[ShortcutEntry]: ...
    def register(self, entry: ShortcutEntry) -> bool: ...
    def unregister(self, shortcut_id: str) -> bool: ...
    def find_conflicts(self) -> list[tuple[ShortcutEntry, ShortcutEntry]]: ...
    def help_text(self) -> str: ...


# ======================================================================
#  Реализация по умолчанию
# ======================================================================
class DefaultShortcutRegistry:
    """Реестр с готовым набором сочетаний для «Суперапп».

    Конфликты (двойная регистрация одного id) запрещены; конфликты по
    комбинации+контексту выявляются find_conflicts() и НЕ блокируют
    регистрацию — UI сам решит, как поступить (например, показать диалог).
    """

    def __init__(self, initial: Iterable[ShortcutEntry] | None = None) -> None:
        self._entries: dict[str, ShortcutEntry] = {}
        if initial is None:
            initial = _default_shortcuts()
        for e in initial:
            # на случай кривых данных в initial — валидация в __post_init__
            self._entries[e.id] = e

    # --- чтение -------------------------------------------------------------
    def get_all(self) -> list[ShortcutEntry]:
        return list(self._entries.values())

    def get_by_id(self, shortcut_id: str) -> ShortcutEntry | None:
        return self._entries.get(shortcut_id)

    def get_by_category(self, category: str) -> list[ShortcutEntry]:
        return [e for e in self._entries.values() if e.category == category]

    def get_by_context(self, context: str) -> list[ShortcutEntry]:
        return [e for e in self._entries.values() if e.context == context]

    # --- запись -------------------------------------------------------------
    def register(self, entry: ShortcutEntry) -> bool:
        """Добавить/заменить по id. True — записано, False — невалидная комбинация."""
        if entry.id in self._entries:
            # перезапись разрешена, но логируем через возвращаемое значение
            self._entries[entry.id] = entry
            return True
        self._entries[entry.id] = entry
        return True

    def unregister(self, shortcut_id: str) -> bool:
        return self._entries.pop(shortcut_id, None) is not None

    # --- конфликты ----------------------------------------------------------
    def find_conflicts(self) -> list[tuple[ShortcutEntry, ShortcutEntry]]:
        """Пары с одинаковой комбинацией в одном контексте.

        Возвращает отсортированные по id пары без дубликатов (A,B) == (B,A).
        """
        seen: dict[tuple[str, str], ShortcutEntry] = {}
        conflicts: list[tuple[ShortcutEntry, ShortcutEntry]] = []
        for e in self._entries.values():
            key = (e.sequence, e.context)
            prev = seen.get(key)
            if prev is None:
                seen[key] = e
            else:
                a, b = sorted((prev, e), key=lambda x: x.id)
                if (a, b) not in conflicts:
                    conflicts.append((a, b))
        return conflicts

    # --- справка ------------------------------------------------------------
    def help_text(self) -> str:
        """Форматированный текст для меню «Справка → Горячие клавиши».

        Группировка по категориям, колонки выровнены по самой длинной комбинации.
        """
        entries = sorted(self._entries.values(), key=lambda e: (e.category, e.id))
        if not entries:
            return "Горячие клавиши не настроены."

        # ширина колонки последовательности
        seq_w = max(len(e.sequence) for e in entries)
        seq_w = max(seq_w, len("Комбинация"))

        lines: list[str] = []
        header = f"{'Комбинация':<{seq_w}}   Описание"
        lines.append(header)
        lines.append("-" * len(header))

        cur_cat: str | None = None
        for e in entries:
            if e.category != cur_cat:
                cur_cat = e.category
                lines.append("")
                lines.append(f"[ {cur_cat} ]")
            lines.append(f"{e.sequence:<{seq_w}}   {e.description}")

        return "\n".join(lines)


# ======================================================================
#  Готовый набор сочетаний для «Суперапп»
# ======================================================================
def _default_shortcuts() -> list[ShortcutEntry]:
    return [
        # --- Файловый менеджер ---
        ShortcutEntry(
            "fm.new_folder", "Ctrl+Shift+N", "Создать папку", CAT_FILE, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "fm.new_file", "Ctrl+Shift+F", "Создать файл", CAT_FILE, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "fm.open", "Return", "Открыть выделенный элемент", CAT_FILE, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "fm.rename", "F2", "Переименовать элемент", CAT_FILE, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "fm.delete_trash", "Delete", "Удалить в корзину", CAT_FILE, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "fm.delete_perm",
            "Shift+Delete",
            "Удалить безвозвратно",
            CAT_FILE,
            CTX_FILEMANAGER,
        ),
        ShortcutEntry(
            "fm.properties",
            "Alt+Return",
            "Свойства элемента",
            CAT_FILE,
            CTX_FILEMANAGER,
        ),
        ShortcutEntry(
            "fm.search", "Ctrl+F", "Поиск файлов и папок", CAT_FILE, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "fm.save_report",
            "Ctrl+S",
            "Сохранить отчёт о процессах",
            CAT_FILE,
            CTX_FILEMANAGER,
        ),
        # --- Навигация ---
        ShortcutEntry("nav.back", "Alt+Left", "Назад", CAT_NAV, CTX_FILEMANAGER),
        ShortcutEntry("nav.forward", "Alt+Right", "Вперёд", CAT_NAV, CTX_FILEMANAGER),
        ShortcutEntry("nav.up", "Alt+Up", "Вверх на уровень", CAT_NAV, CTX_FILEMANAGER),
        ShortcutEntry(
            "nav.home", "Alt+Home", "Корень «Суперапп»", CAT_NAV, CTX_FILEMANAGER
        ),
        # --- Правка ---
        ShortcutEntry("edit.cut", "Ctrl+X", "Вырезать", CAT_EDIT, CTX_FILEMANAGER),
        ShortcutEntry("edit.copy", "Ctrl+C", "Копировать", CAT_EDIT, CTX_FILEMANAGER),
        ShortcutEntry("edit.paste", "Ctrl+V", "Вставить", CAT_EDIT, CTX_FILEMANAGER),
        ShortcutEntry(
            "edit.select_all", "Ctrl+A", "Выделить всё", CAT_EDIT, CTX_FILEMANAGER
        ),
        ShortcutEntry(
            "edit.invert",
            "Ctrl+I",
            "Инвертировать выделение",
            CAT_EDIT,
            CTX_FILEMANAGER,
        ),
        # --- Вид ---
        ShortcutEntry("view.refresh", "F5", "Обновить", CAT_VIEW, CTX_GLOBAL),
        ShortcutEntry(
            "view.toggle_hidden",
            "Ctrl+H",
            "Показывать скрытые",
            CAT_VIEW,
            CTX_FILEMANAGER,
        ),
        ShortcutEntry("view.clear", "Ctrl+L", "Очистить экран", CAT_VIEW, CTX_TERMINAL),
        # --- Терминал ---
        ShortcutEntry("term.open", "F4", "Открыть терминал", CAT_TERM, CTX_GLOBAL),
        ShortcutEntry(
            "term.interrupt",
            "Ctrl+C",
            "Прервать команду (в терминале)",
            CAT_TERM,
            CTX_TERMINAL,
        ),
        ShortcutEntry(
            "term.eof", "Ctrl+D", "Конец ввода (EOF)", CAT_TERM, CTX_TERMINAL
        ),
        ShortcutEntry(
            "term.help", "F1", "Справка по командам терминала", CAT_TERM, CTX_TERMINAL
        ),
        # --- Мониторинг ---
        ShortcutEntry(
            "mon.start", "Ctrl+M", "Запустить мониторинг процессов", CAT_MON, CTX_GLOBAL
        ),
        ShortcutEntry(
            "mon.gpu",
            "Ctrl+G",
            "Всплывающее окно: видеокарта (вар. 5)",
            CAT_MON,
            CTX_GLOBAL,
        ),
        ShortcutEntry(
            "mon.log", "Ctrl+Shift+L", "Открыть лог-файл", CAT_MON, CTX_GLOBAL
        ),
        # --- Приложение ---
        ShortcutEntry("app.about", "Ctrl+F1", "О программе", CAT_APP, CTX_GLOBAL),
        ShortcutEntry(
            "app.hotkeys", "F1", "Горячие клавиши (справка)", CAT_APP, CTX_GLOBAL
        ),
        ShortcutEntry("app.exit", "Ctrl+Q", "Выход из приложения", CAT_APP, CTX_GLOBAL),
    ]
