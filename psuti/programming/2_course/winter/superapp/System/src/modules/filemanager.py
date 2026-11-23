import os
import shutil
import subprocess
import sys
import time
from typing import Optional

from PyQt5.QtCore import QFileInfo, QMimeData, QSize, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDialog,
    QDialogButtonBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)
_PKG_ROOT = os.path.dirname(_SRC)
for _p in (_PKG_ROOT, _SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import src.settings as cfg


class FolderListWidget(QListWidget):
    """Список-плитки с поддержкой Drag and Drop (Задание 3).

    Поддерживаются два вида перетаскивания:
    - внутреннее: плитку «Суперапп» тянут на другую папку или на фон
      (операция «переместить»);
    - внешнее: файлы перетаскивают из файлового менеджера ОС
      (операция «копировать»).

    Сам виджет файлов не трогает: он лишь превращает сброс в сигнал
    paths_dropped(пути, целевая_папка, из_приложения), а реальное
    перемещение выполняет filemanager_func._on_paths_dropped.
    """

    paths_dropped = pyqtSignal(list, str, bool)  # (пути, цель, из «Суперапп»?)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._apply_dnd()
        self.current_dir: str = ""  # цель сброса «на фон»

    def _apply_dnd(self) -> None:
        """Включить перетаскивание плиток и приём сбросов.

        Отдельный метод, потому что setMovement(Static) (её вызывает
        _build_central, чтобы плитки нельзя было сдвинуть визуально)
        в Qt заодно сбрасывает dragEnabled и переключает режим
        в DropOnly — без повторного включения тянуть плитки нельзя.
        """
        self.setDragEnabled(True)  # плитки можно тянуть
        self.setAcceptDrops(True)  # и на них можно бросать
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QListWidget.DragDrop)

    def setMovement(self, movement) -> None:
        """После смены movement восстановить настройки Drag and Drop."""
        super().setMovement(movement)
        self._apply_dnd()

    # --- что отдаём при перетаскивании наружу ---
    def mimeData(self, items):
        """Mime-данные перетаскивания с URL файлов.

        Фирменный формат Qt (x-qabstractitemmodeldatalist) понимают
        только Qt-приложения, поэтому добавляем обычные URL — благодаря
        им плитки можно перетаскивать и в ОС, а собственный
        drop-обработчик получает пути источников из mime-данных.
        """
        mime = super().mimeData(items)
        if mime is None:
            mime = QMimeData()
        urls = []
        for it in items:
            p = it.data(cfg.FILEMANAGER_ROLE_PATH)
            if p:
                urls.append(QUrl.fromLocalFile(p))
        if urls:
            mime.setUrls(urls)
        return mime

    # --- приём перетаскивания ---
    def dragEnterEvent(self, event) -> None:
        if self._is_supported(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event) -> None:
        if self._is_supported(event):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event) -> None:
        mime = event.mimeData()
        internal = event.source() is self or mime.hasFormat(
            "application/x-qabstractitemmodeldatalist"
        )
        sources = [u.toLocalFile() for u in mime.urls() if u.isLocalFile()]
        if internal and not sources:
            for it in self.selectedItems():
                p = it.data(cfg.FILEMANAGER_ROLE_PATH)
                if p:
                    sources.append(p)
        target = self._drop_target(event.pos())
        if sources and target:
            event.setDropAction(Qt.MoveAction if internal else Qt.CopyAction)
            event.accept()
            self.paths_dropped.emit(sources, target, internal)
        else:
            event.ignore()

    # --- утилиты события ---
    def _is_supported(self, event) -> bool:
        """Внутреннее перетаскивание плиток или внешние URL файлов."""
        mime = event.mimeData()
        return (
            event.source() is self
            or mime.hasUrls()
            or mime.hasFormat("application/x-qabstractitemmodeldatalist")
        )

    def _drop_target(self, pos) -> str:
        """Цель: папка под курсором либо текущий каталог (сброс на фон)."""
        item = self.itemAt(pos)
        if item is not None and item.data(cfg.FILEMANAGER_ROLE_KIND) == "dir":
            return item.data(cfg.FILEMANAGER_ROLE_PATH)
        return self.current_dir


class filemanager_ui(QMainWindow):
    """Интерфейс Файлового менеджера"""

    # сигналы-запросы (UI сообщает, что хочет сделать; логика — в func)
    navigate_requested = pyqtSignal(str)
    open_requested = pyqtSignal(str, bool)  # (path, ctrl_held)
    terminal_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    back_requested = pyqtSignal()
    forward_requested = pyqtSignal()
    up_requested = pyqtSignal()
    about_requested = pyqtSignal()
    hotkeys_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(cfg.FILEMANAGER_TITLE)
        self.resize(*cfg.FILEMANAGER_SIZE)

        self._actions: dict[str, QAction] = {}
        self._custom_folder_icon: Optional[QIcon] = None
        self._custom_file_icon: Optional[QIcon] = None
        _folder_url = getattr(cfg, "FILEMANAGER_FOLDER_ICON_URL", "")
        _file_url = getattr(cfg, "FILEMANAGER_FILE_ICON_URL", "")
        if _folder_url or _file_url:
            self._custom_folder_icon = QIcon(_folder_url)
            self._custom_file_icon = QIcon(_file_url)

        self._build_actions()
        self._build_menubar()
        self._build_toolbar()
        self._build_central()

    # --- действия ---
    def _build_actions(self) -> None:
        st = self.style()

        def act(
            name: str,
            text: str,
            shortcut: str = "",
            icon: Optional[QIcon] = None,
            tip: str = "",
        ) -> QAction:
            a = QAction(icon or QIcon(), text, self)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            a.setStatusTip(tip or text)
            self._actions[name] = a
            return a

        # Файл
        act(
            "new_folder",
            "Создать папку",
            "Ctrl+Shift+N",
            st.standardIcon(QStyle.SP_DirIcon),
        )
        act(
            "new_file",
            "Создать файл",
            "Ctrl+Shift+F",
            st.standardIcon(QStyle.SP_FileIcon),
        )
        act(
            "search",
            "Поиск файлов и папок...",
            "Ctrl+F",
            tip="Поиск во вложенных папках «Суперапп»",
        )
        act(
            "open_terminal",
            "Открыть терминал",
            "F4",
            st.standardIcon(QStyle.SP_CommandLink),
        )
        act(
            "open_monitoring",
            "Мониторинг процессов",
            "Ctrl+M",
            st.standardIcon(QStyle.SP_ToolBarHorizontalExtensionButton),
        )
        act("exit", "Выход", "Ctrl+Q")

        # Правка
        act("cut", "Вырезать", "Ctrl+X")
        act("copy", "Копировать", "Ctrl+C")
        act("paste", "Вставить", "Ctrl+V")
        act("select_all", "Выделить всё", "Ctrl+A")

        # Операции над выбранным
        act("open", "Открыть", "Return")
        act("open_in_popup", "Открыть в новом окне")
        act("rename", "Переименовать", "F2")
        act("delete_trash", "Удалить в корзину", "Delete")
        act("delete_perm", "Удалить безвозвратно", "Shift+Delete")
        act("properties", "Свойства", "Alt+Return")

        # Вид
        act("refresh", "Обновить", "F5", st.standardIcon(QStyle.SP_BrowserReload))
        act("toggle_hidden", "Показывать скрытые", "Ctrl+H")

        # Переход
        act("back", "Назад", "Alt+Left", st.standardIcon(QStyle.SP_ArrowLeft))
        act("forward", "Вперёд", "Alt+Right", st.standardIcon(QStyle.SP_ArrowRight))
        act("up", "Вверх", "Alt+Up", st.standardIcon(QStyle.SP_ArrowUp))
        act(
            "removable",
            "Съёмные носители...",
            "",
            st.standardIcon(QStyle.SP_DriveHDIcon),
            tip="Подключённые к ОС съёмные носители",
        )

        # Справка
        act("hotkeys", "Горячие клавиши", "F1")
        act("about", "О программе")

    # --- меню ---
    def _build_menubar(self) -> None:
        mb: QMenuBar = self.menuBar()
        A = self._actions.__getitem__

        m_file = mb.addMenu("Файл")
        m_file.addAction(A("new_folder"))
        m_file.addAction(A("new_file"))
        m_file.addSeparator()
        m_file.addAction(A("search"))
        m_file.addSeparator()
        m_file.addAction(A("open_terminal"))
        m_file.addAction(A("open_monitoring"))
        m_file.addSeparator()
        m_file.addAction(A("exit"))

        m_edit = mb.addMenu("Правка")
        m_edit.addAction(A("cut"))
        m_edit.addAction(A("copy"))
        m_edit.addAction(A("paste"))
        m_edit.addSeparator()
        m_edit.addAction(A("rename"))
        m_edit.addAction(A("delete_trash"))
        m_edit.addAction(A("delete_perm"))
        m_edit.addSeparator()
        m_edit.addAction(A("select_all"))

        m_view = mb.addMenu("Вид")
        m_view.addAction(A("refresh"))
        m_view.addAction(A("toggle_hidden"))

        m_go = mb.addMenu("Переход")
        m_go.addAction(A("back"))
        m_go.addAction(A("forward"))
        m_go.addAction(A("up"))
        m_go.addSeparator()
        m_go.addAction(A("removable"))

        m_term = mb.addMenu("Терминал")
        m_term.addAction(A("open_terminal"))

        m_mon = mb.addMenu("Мониторинг")
        m_mon.addAction(A("open_monitoring"))

        m_help = mb.addMenu("Справка")
        m_help.addAction(A("hotkeys"))
        m_help.addSeparator()
        m_help.addAction(A("about"))

    # --- тулбар: навигация + путь ---
    def _build_toolbar(self) -> None:
        tb = QToolBar("Навигация")
        tb.setMovable(False)
        tb.setIconSize(QSize(16, 16))
        self.addToolBar(tb)
        A = self._actions.__getitem__

        tb.addAction(A("back"))
        tb.addAction(A("forward"))
        tb.addAction(A("up"))
        tb.addAction(A("refresh"))
        tb.addSeparator()

        self.path_bar = QLineEdit()
        self.path_bar.setPlaceholderText("Путь...")
        self.path_bar.setToolTip("Текущий путь. Enter — перейти.")
        tb.addWidget(self.path_bar)

    # --- центральная область: плитки папок ---
    def _build_central(self) -> None:
        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        self.list = FolderListWidget()
        self.list.setViewMode(QListWidget.IconMode)
        self.list.setIconSize(QSize(*cfg.FILEMANAGER_ICON_SIZE))
        self.list.setGridSize(QSize(*cfg.FILEMANAGER_GRID_SIZE))
        self.list.setResizeMode(QListWidget.Adjust)
        self.list.setMovement(QListWidget.Static)
        self.list.setUniformItemSizes(True)
        self.list.setSpacing(8)
        # рамка убрана — чище, как в Thunar
        self.list.setFrameShape(QListWidget.NoFrame)
        lay.addWidget(self.list)

        self.setCentralWidget(central)

    # --- контекстное меню (общее поведение UI; те же QAction, что и в меню) ---
    def contextMenuEvent(self, event) -> None:
        item = self.list.itemAt(self.list.viewport().mapFromGlobal(event.globalPos()))
        A = self._actions.__getitem__

        menu = QMenu(self)
        if item is not None:
            menu.addAction(A("open"))
            menu.addAction(A("open_in_popup"))
            menu.addSeparator()
            menu.addAction(A("rename"))
            menu.addAction(A("delete_trash"))
            menu.addAction(A("delete_perm"))
            menu.addSeparator()
            menu.addAction(A("properties"))
            menu.addSeparator()
        menu.addAction(A("new_folder"))
        menu.addAction(A("new_file"))
        menu.exec_(event.globalPos())

    # --- вкл/выкл навигации (общее поведение UI) ---
    def update_nav_state(self, can_back: bool, can_forward: bool, can_up: bool) -> None:
        self._actions["back"].setEnabled(can_back)
        self._actions["forward"].setEnabled(can_forward)
        self._actions["up"].setEnabled(can_up)


class filemanager_func(filemanager_ui):
    """Логика файлового менеджера поверх UI.

    Наследует UI, подключает сигналы к реальным действиям: чтение каталога,
    навигация, создание/переименование/удаление, корзина, поиск, буфер
    обмена, открытие папок/файлов, запуск popup.py / terminal.py /
    monitoring.py, защита папки System.

    Журнал посещений и операций (куда заходил, что создавал/удалял)
    пишется в fm_journal.log рядом с System (cfg.FM_JOURNAL_PATH).
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # история навигации
        self._history: list[str] = []
        self._history_pos: int = -1
        # показывать скрытые (точечные) имена
        self._show_hidden: bool = False
        # буфер обмена для вырезать/копировать: (операция, путь)
        self._clip: list[tuple[str, str]] = []
        # корни съёмных носителей (чтобы «Вверх» не уводил из них в ОС)
        self._removable_roots: set[str] = set()

        self._journal("start", "запуск файлового менеджера")

        self._wire_signals()
        self._update_nav()

    # --- журнал посещений и операций ФМ (Лог-файл, Задание) ---
    def _journal(self, action: str, details: str) -> None:
        """Записать событие в журнал посещений/операций ФМ.

        Формат: <дата время> <действие> <подробности>. Сбои записи в журнал
        (например, нет места на диске) не должны ломать сам менеджер —
        ошибки молча игнорируются.
        """
        try:
            with open(cfg.FM_JOURNAL_PATH, "a", encoding="utf-8") as f:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(
                    "{ts}  {action:10}  {details}\n".format(
                        ts=ts, action=action, details=details
                    )
                )
        except OSError:
            pass  # журнал вспомогательный — не прерываем работу ФМ

    # --- подключение сигналов UI -> логика ---
    def _wire_signals(self) -> None:
        A = self._actions.__getitem__

        # навигация
        A("back").triggered.connect(self._go_back)
        A("forward").triggered.connect(self._go_forward)
        A("up").triggered.connect(self._go_up)
        A("removable").triggered.connect(self._open_removable)
        A("refresh").triggered.connect(self._reload)
        self.path_bar.returnPressed.connect(self._on_path_entered)
        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)

        # Drag and Drop: виджет сообщил о сбросе — выполняем перенос
        self.list.paths_dropped.connect(self._on_paths_dropped)

        # операции над файлами
        A("new_folder").triggered.connect(self._new_folder)
        A("new_file").triggered.connect(self._new_file)
        A("search").triggered.connect(self._search)
        A("open").triggered.connect(self._open_selected)
        A("open_in_popup").triggered.connect(self._open_selected_in_popup)
        A("rename").triggered.connect(self._rename)
        A("delete_trash").triggered.connect(self._delete_trash)
        A("delete_perm").triggered.connect(self._delete_perm)
        A("properties").triggered.connect(self._properties)

        # правка
        A("cut").triggered.connect(lambda: self._clip_set("cut"))
        A("copy").triggered.connect(lambda: self._clip_set("copy"))
        A("paste").triggered.connect(self._paste)
        A("select_all").triggered.connect(self.list.selectAll)

        # вид
        A("toggle_hidden").setCheckable(True)
        A("toggle_hidden").setChecked(False)
        A("toggle_hidden").triggered.connect(self._toggle_hidden)

        # отдельные процессы
        A("open_terminal").triggered.connect(self._open_terminal)
        A("open_monitoring").triggered.connect(self._open_monitoring)
        A("exit").triggered.connect(self.close)

        # справка
        A("about").triggered.connect(self._show_about)
        A("hotkeys").triggered.connect(self._show_hotkeys)

    def navigate(self, path: str, *, push_history: bool = True) -> bool:
        """Перейти в каталог path. Возвращает True при успехе."""
        path = os.path.abspath(path)
        if not os.path.exists(path):
            self._error(cfg.MSG_NO_SUCH_PATH.format(path=path))
            return False
        if not os.path.isdir(path):
            self._error(cfg.MSG_NOT_A_DIR.format(path=path))
            return False

        self.path_bar.setText(path)
        if push_history:
            self._push_history(path)
        self._journal("visit", "переход в каталог: " + path)
        self._populate(path)
        self._update_nav()
        return True

    def _push_history(self, path: str) -> None:
        # обрезаем «вперёд»
        self._history = self._history[: self._history_pos + 1]
        if self._history and self._history[-1] == path:
            return
        self._history.append(path)
        self._history_pos = len(self._history) - 1

    def _go_back(self) -> None:
        if self._history_pos > 0:
            self._history_pos -= 1
            self.navigate(self._history[self._history_pos], push_history=False)
            self._update_nav()

    def _go_forward(self) -> None:
        if self._history_pos < len(self._history) - 1:
            self._history_pos += 1
            self.navigate(self._history[self._history_pos], push_history=False)
            self._update_nav()

    def _go_up(self) -> None:
        cur = os.path.abspath(self.path_bar.text().strip())
        if not cur:
            return
        # не поднимаемся выше корня «Суперапп»
        if cur == os.path.abspath(cfg.SUPERAPP_ROOT):
            return
        # и выше корня съёмного носителя (не выходим в ОС через «Вверх»)
        if cur in self._removable_roots:
            return
        up = os.path.dirname(cur) or "/"
        self.navigate(up)

    def _on_path_entered(self) -> None:
        path = self.path_bar.text().strip()
        if path:
            self.navigate(path)

    def _reload(self) -> None:
        path = self.path_bar.text().strip()
        if path:
            self._populate(path)

    def _update_nav(self) -> None:
        cur = self.path_bar.text().strip()
        can_up = bool(cur) and os.path.abspath(cur) != os.path.abspath(
            cfg.SUPERAPP_ROOT
        )
        self.update_nav_state(
            can_back=self._history_pos > 0,
            can_forward=self._history_pos < len(self._history) - 1,
            can_up=can_up,
        )

    def _populate(self, path: str) -> None:
        self.list.current_dir = path  # цель Drag and Drop «на фон»
        self.list.clear()
        try:
            entries = os.listdir(path)
        except OSError as e:
            self._error(cfg.MSG_OPEN_ERROR.format(name=path, err=e))
            return

        # скрытые фильтруем; папки — впереди файлов
        if not self._show_hidden:
            entries = [n for n in entries if not n.startswith(".")]
        entries.sort(
            key=lambda n: (not os.path.isdir(os.path.join(path, n)), n.lower())
        )

        for name in entries:
            full = os.path.join(path, name)
            is_dir = os.path.isdir(full)
            protected = name in cfg.PROTECTED_NAMES

            icon = self._icon_for(full, is_dir)
            item = QListWidgetItem(icon, name)
            item.setData(cfg.FILEMANAGER_ROLE_PATH, full)
            item.setData(cfg.FILEMANAGER_ROLE_KIND, "dir" if is_dir else "file")
            item.setData(cfg.FILEMANAGER_ROLE_PROTECTED, protected)
            self.list.addItem(item)

    def _icon_for(self, path: str, is_dir: bool) -> QIcon:
        if (
            is_dir
            and self._custom_folder_icon is not None
            and not self._custom_folder_icon.isNull()
        ):
            return self._custom_folder_icon
        return self._custom_file_icon

    def _toggle_hidden(self) -> None:
        self._show_hidden = self._actions["toggle_hidden"].isChecked()
        self._reload()

    def _selected_item(self) -> Optional[QListWidgetItem]:
        items = self.list.selectedItems()
        return items[0] if items else None

    def _current_dir(self) -> str:
        return os.path.abspath(self.path_bar.text().strip() or cfg.SUPERAPP_ROOT)

    def _new_folder(self) -> None:
        """Ctrl+Shift+N — создать папку (запрос имени через диалог)."""
        name, ok = QInputDialog.getText(
            self, "Новая папка", "Имя папки:", QLineEdit.Normal, ""
        )
        if ok and name.strip():
            self._create_entry(name.strip(), is_dir=True)

    def _new_file(self) -> None:
        """Ctrl+Shift+F — создать файл (запрос имени через диалог)."""
        name, ok = QInputDialog.getText(
            self, "Новый файл", "Имя файла:", QLineEdit.Normal, ""
        )
        if ok and name.strip():
            self._create_entry(name.strip(), is_dir=False)

    def _create_entry(self, name: str, is_dir: bool) -> bool:
        """Создать папку (is_dir=True) или пустой файл в текущем каталоге."""
        if not name or name in (".", "..") or "/" in name or "\0" in name:
            self._error(cfg.MSG_BAD_NAME.format(name=name))
            return False
        if name in cfg.PROTECTED_NAMES or name == cfg.TRASH_FOLDER:
            self._error(cfg.MSG_PROTECTED_NAME.format(name=name))
            return False

        full = os.path.join(self._current_dir(), name)
        if os.path.exists(full):
            self._error(cfg.MSG_EXISTS.format(name=name))
            return False
        try:
            if is_dir:
                os.mkdir(full)
            else:
                with open(full, "x", encoding="utf-8"):
                    pass
        except OSError as e:
            self._error(cfg.MSG_CREATE_FAIL.format(name=name, err=e))
            return False
        self._journal(
            "create",
            "создан {what}: {path}".format(
                what="каталог" if is_dir else "файл", path=full
            ),
        )
        self._reload()
        return True

    def _rename(self) -> None:
        """F2 — переименовать выбранный элемент."""
        item = self._selected_item()
        if item is None:
            self._info(cfg.MSG_NO_SELECTION)
            return
        old = item.text()
        if bool(item.data(cfg.FILEMANAGER_ROLE_PROTECTED)):
            self._error(cfg.MSG_SYSTEM_PROTECTED.format(name=old))
            return

        new, ok = QInputDialog.getText(
            self, "Переименование", f"Новое имя для «{old}»:", QLineEdit.Normal, old
        )
        if not ok:
            return
        new = new.strip()
        if not new or new == old:
            return
        if new in cfg.PROTECTED_NAMES or new == cfg.TRASH_FOLDER:
            self._error(cfg.MSG_PROTECTED_NAME.format(name=new))
            return
        base = self._current_dir()
        if os.path.exists(os.path.join(base, new)):
            self._error(cfg.MSG_EXISTS.format(name=new))
            return
        try:
            os.rename(os.path.join(base, old), os.path.join(base, new))
        except OSError as e:
            self._error(cfg.MSG_RENAME_FAIL.format(name=old, err=e))
            return
        self._journal(
            "rename",
            "«{old}» -> «{new}» (в {base})".format(old=old, new=new, base=base),
        )
        self._reload()

    def _delete_trash(self) -> None:
        """Delete — переместить выбранный элемент в Корзину."""
        item = self._selected_item()
        if item is None:
            self._info(cfg.MSG_NO_SELECTION)
            return
        name = item.text()
        if bool(item.data(cfg.FILEMANAGER_ROLE_PROTECTED)):
            self._error(cfg.MSG_SYSTEM_PROTECTED.format(name=name))
            return

        src = item.data(cfg.FILEMANAGER_ROLE_PATH)
        # Корзина обязана существовать
        os.makedirs(cfg.TRASH_PATH, exist_ok=True)
        dst = os.path.join(cfg.TRASH_PATH, name)
        # имя в Корзине не должно конфликтовать
        if os.path.exists(dst):
            dst = os.path.join(cfg.TRASH_PATH, f"{name} ({self._stamp()})")
        try:
            shutil.move(src, dst)
        except OSError as e:
            self._error(cfg.MSG_TRASH_FAIL.format(name=name, err=e))
            return
        self._journal(
            "trash",
            "в корзину: {src} -> {dst}".format(src=src, dst=dst),
        )
        self._reload()

    def _delete_perm(self) -> None:
        """Shift+Delete — удалить безвозвратно (с подтверждением)."""
        item = self._selected_item()
        if item is None:
            self._info(cfg.MSG_NO_SELECTION)
            return
        name = item.text()
        if bool(item.data(cfg.FILEMANAGER_ROLE_PROTECTED)):
            self._error(cfg.MSG_SYSTEM_PROTECTED.format(name=name))
            return

        btn = QMessageBox.question(
            self, "Удаление", cfg.MSG_DELETE_CONFIRM.format(name=name)
        )
        if btn != QMessageBox.Yes:
            return
        src = item.data(cfg.FILEMANAGER_ROLE_PATH)
        try:
            if os.path.isdir(src):
                shutil.rmtree(src)
            else:
                os.remove(src)
        except OSError as e:
            self._error(cfg.MSG_DELETE_FAIL.format(name=name, err=e))
            return
        self._journal(
            "delete",
            "безвозвратно удалено: {path}".format(path=src),
        )
        self._reload()

    def _properties(self) -> None:
        """Alt+Return — свойства выбранного элемента."""
        item = self._selected_item()
        if item is None:
            self._info(cfg.MSG_NO_SELECTION)
            return
        path = item.data(cfg.FILEMANAGER_ROLE_PATH)
        name = item.text()
        try:
            st = os.stat(path)
            mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime))
            if os.path.isdir(path):
                n_files = sum(len(files) for _, _, files in os.walk(path))
                size = sum(
                    os.path.getsize(os.path.join(r, f))
                    for r, _, files in os.walk(path)
                    for f in files
                )
                kind = "Папка"
                extra = f"Объектов внутри: {n_files}"
            else:
                size = st.st_size
                kind = "Файл"
                extra = ""
        except OSError as e:
            self._error(cfg.MSG_OPEN_ERROR.format(name=name, err=e))
            return

        text = (
            f"{kind}: {name}\n\n"
            f"Путь: {path}\n"
            f"Размер: {self._human_size(size)} ({size} байт)\n"
            f"Изменён: {mtime}"
        )
        if extra:
            text += f"\n{extra}"
        QMessageBox.information(self, "Свойства", text)

    @staticmethod
    def _human_size(n: float) -> str:
        for unit in ("Б", "КБ", "МБ", "ГБ", "ТБ"):
            if n < 1024 or unit == "ТБ":
                return f"{n:.0f} {unit}" if unit == "Б" else f"{n:.1f} {unit}"
            n /= 1024
        return f"{n} Б"

    @staticmethod
    def _stamp() -> str:
        return time.strftime("%H%M%S")

    def _clip_set(self, op: str) -> None:
        items = self.list.selectedItems()
        if not items:
            self._info(cfg.MSG_NO_SELECTION)
            return
        self._clip = [
            (op, it.data(cfg.FILEMANAGER_ROLE_PATH))
            for it in items
            if not bool(it.data(cfg.FILEMANAGER_ROLE_PROTECTED))
        ]

    def _paste(self) -> None:
        """Вставить вырезанное/скопированное в текущий каталог."""
        if not self._clip:
            return
        dst_dir = self._current_dir()
        for op, src in self._clip:
            if not os.path.exists(src):
                continue
            name = os.path.basename(src.rstrip("/"))
            dst = os.path.join(dst_dir, name)
            if os.path.abspath(src) == os.path.abspath(dst):
                continue
            if os.path.exists(dst):
                dst = os.path.join(dst_dir, f"{name} ({self._stamp()})")
            try:
                if op == "cut":
                    shutil.move(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except OSError as e:
                self._error(cfg.MSG_PASTE_FAIL.format(name=name, err=e))
                continue
            self._journal(
                "move" if op == "cut" else "copy",
                "{src} -> {dst}".format(src=src, dst=dst),
            )
        if any(op == "cut" for op, _ in self._clip):
            self._clip = []
        self._reload()

    def _on_paths_dropped(self, paths: list, target_dir: str, from_app: bool) -> None:
        """Перетаскивание: переместить объекты «Суперапп» / скопировать извне.

        Внутренние перетаскивания перемещают объекты (плитку на папку или
        на фон), внешние — копируют внутрь «Суперапп». Папка System и
        Корзина в корне не участвуют ни как источник, ни как приёмник.
        """
        if not paths or not target_dir:
            return
        target_dir = os.path.abspath(target_dir)

        # приёмник: внутрь System ничего помещать нельзя
        app_root = os.path.abspath(cfg.APP_ROOT)
        if target_dir == app_root or target_dir.startswith(app_root + os.sep):
            self._error(cfg.MSG_DND_DROP_SYSTEM)
            return

        # источники: System/Корзина перетаскивать нельзя (как и переименовывать)
        if from_app:
            allowed = [
                p
                for p in paths
                if os.path.basename(p.rstrip(os.sep)) not in cfg.PROTECTED_NAMES
                and os.path.basename(p.rstrip(os.sep)) != cfg.TRASH_FOLDER
            ]
            if not allowed:
                self._error(cfg.MSG_SYSTEM_PROTECTED.format(name=cfg.SYSTEM_FOLDER))
                return
            paths = allowed

        for src in paths:
            src = os.path.abspath(src)
            if not os.path.exists(src):
                continue  # объект уже исчез (например, второй перенос)
            # перекладывание папки саму в себя лишено смысла
            if os.path.abspath(src) == target_dir:
                continue
            if from_app and os.path.dirname(src) == target_dir:
                continue
            # внутрь собственного содержимого папку не кладём
            if os.path.isdir(src) and target_dir.startswith(src + os.sep):
                continue

            name = os.path.basename(src.rstrip(os.sep))
            dst = os.path.join(target_dir, name)
            if os.path.exists(dst):
                dst = os.path.join(target_dir, f"{name} ({self._stamp()})")
            try:
                if from_app:
                    shutil.move(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
            except OSError as e:
                self._error(cfg.MSG_DND_MOVE_FAIL.format(name=name, err=e))
                continue
            self._journal(
                "dnd-move" if from_app else "dnd-copy",
                "{src} -> {dst}".format(src=src, dst=dst),
            )
        self._reload()

    def _do_search(self, pattern: str) -> list[str]:
        """Рекурсивный поиск по подстроке от корня «Суперапп»."""
        pattern = pattern.strip().lower()
        if not pattern:
            return []
        matches: list[str] = []
        root = os.path.abspath(cfg.SUPERAPP_ROOT)
        app_root = os.path.abspath(cfg.APP_ROOT)
        for dirpath, dirnames, filenames in os.walk(root):
            # внутрь System не заходим — это код приложения
            if os.path.abspath(dirpath) == app_root:
                dirnames[:] = []
                continue
            for n in dirnames + filenames:
                if pattern in n.lower():
                    matches.append(os.path.join(dirpath, n))
        return matches

    def _search(self) -> None:
        """Ctrl+F — диалог поиска; двойной клик по результату — переход."""
        pattern, ok = QInputDialog.getText(
            self, "Поиск", "Что искать (часть имени):", QLineEdit.Normal, ""
        )
        if not ok or not pattern.strip():
            return
        matches = self._do_search(pattern)

        dlg = QDialog(self)
        dlg.setWindowTitle(f"Поиск: «{pattern}» — найдено {len(matches)}")
        dlg.resize(520, 360)
        lay = QVBoxLayout(dlg)
        lay.addWidget(QLabel("Двойной клик по папке — перейти к ней."))
        lw = QListWidget()
        lay.addWidget(lw, 1)
        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(dlg.reject)
        btns.clicked.connect(dlg.reject)
        lay.addWidget(btns)

        for m in matches:
            it = QListWidgetItem(self._icon_for(m, os.path.isdir(m)), m)
            it.setData(cfg.FILEMANAGER_ROLE_PATH, m)
            lw.addItem(it)

        def _open_found(cur: QListWidgetItem) -> None:
            path = cur.data(cfg.FILEMANAGER_ROLE_PATH)
            if os.path.isdir(path):
                self.navigate(path)
                dlg.accept()

        lw.itemDoubleClicked.connect(_open_found)
        dlg.exec_()

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        path = item.data(cfg.FILEMANAGER_ROLE_PATH) or ""
        kind = item.data(cfg.FILEMANAGER_ROLE_KIND)
        protected = bool(item.data(cfg.FILEMANAGER_ROLE_PROTECTED))
        # Ctrl зажат? — определяем через глобальное состояние клавиатуры
        ctrl = bool(QApplication.queryKeyboardModifiers() & Qt.ControlModifier)

        if protected:
            self._error(cfg.MSG_SYSTEM_PROTECTED.format(name=item.text()))
            return

        if kind == "dir":
            if ctrl:
                self._open_in_popup(path)
            else:
                self.navigate(path)
        else:
            self._open_file(path)

    def _open_selected(self) -> None:
        """Return / контекстное меню — открыть выбранный элемент."""
        item = self._selected_item()
        if item is None:
            self._info(cfg.MSG_NO_SELECTION)
            return
        self._on_item_double_clicked(item)

    def _open_selected_in_popup(self) -> None:
        """Контекстное меню — открыть выбранную папку в новом окне."""
        item = self._selected_item()
        if item is None:
            self._info(cfg.MSG_NO_SELECTION)
            return
        if bool(item.data(cfg.FILEMANAGER_ROLE_PROTECTED)):
            self._error(cfg.MSG_SYSTEM_PROTECTED.format(name=item.text()))
            return
        if item.data(cfg.FILEMANAGER_ROLE_KIND) != "dir":
            self._info(cfg.MSG_NOT_A_DIR.format(path=item.text()))
            return
        self._open_in_popup(item.data(cfg.FILEMANAGER_ROLE_PATH))

    def _open_in_popup(self, path: str) -> None:
        """Ctrl+двойной клик: открыть папку в новом окне (popup.py)."""
        if not os.path.exists(cfg.POPUP_SCRIPT):
            self._error(f"Не найден popup.py:\n{cfg.POPUP_SCRIPT}")
            return
        try:
            subprocess.Popen(
                [sys.executable, cfg.POPUP_SCRIPT, "--folder", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            self._error(f"Не удалось открыть новое окно:\n{e}")

    def _open_file(self, path: str) -> None:
        """Открыть файл средствами ОС (xdg-open)."""
        try:
            subprocess.Popen(
                ["xdg-open", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            # запасной вариант — показать в диалоге
            self._error(cfg.MSG_OPEN_ERROR.format(name=path, err=e))

    def _open_terminal(self) -> None:
        """Терминал — отдельное окно (terminal.py)."""
        if not os.path.exists(cfg.TERMINAL_SCRIPT):
            self._error(f"Не найден terminal.py:\n{cfg.TERMINAL_SCRIPT}")
            return
        try:
            subprocess.Popen(
                [sys.executable, cfg.TERMINAL_SCRIPT],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            self._error(f"Не удалось открыть терминал:\n{e}")

    def _open_monitoring(self) -> None:
        """Мониторинг процессов — отдельное окно (monitoring.py)."""
        if not os.path.exists(cfg.MONITORING_SCRIPT):
            self._error(f"Не найден monitoring.py:\n{cfg.MONITORING_SCRIPT}")
            return
        try:
            subprocess.Popen(
                [sys.executable, cfg.MONITORING_SCRIPT],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            self._error(f"Не удалось открыть мониторинг:\n{e}")

    @staticmethod
    def _list_removable() -> list[tuple[str, str, str]]:
        """Съёмные носители, подключённые к ОС.

        Читается таблица монтирования ядра (/proc/mounts, запасной
        вариант — /etc/mtab). Съёмным считается носитель с «настоящей»
        файловой системой, смонтированный под /media, /run/media или
        /mnt, либо подключённый как usb-/mmc-устройство. Возвращает
        список кортежей (точка монтирования, устройство, файловая система).
        """
        real_fs = {
            "vfat",
            "exfat",
            "ntfs",
            "ntfs3",
            "fuseblk",
            "ext2",
            "ext3",
            "ext4",
            "btrfs",
            "f2fs",
            "xfs",
            "iso9660",
            "udf",
        }
        lines: list[str] = []
        for mtab in ("/proc/mounts", "/etc/mtab"):
            try:
                with open(mtab, encoding="utf-8") as f:
                    lines = f.readlines()
                break
            except OSError:
                continue
        if not lines:
            return []

        found: dict[str, tuple[str, str, str]] = {}
        for line in lines:
            parts = line.split()
            if len(parts) < 3:
                continue
            dev, mount, fstype = parts[0], parts[1], parts[2]
            # восьмеричные последовательности в точке монтирования
            mount = mount.replace("\\040", " ").replace("\\011", "\t")
            if fstype not in real_fs:
                continue  # proc, sysfs, tmpfs и прочие псевдоФС
            if mount == "/" or mount.startswith("/boot"):
                continue  # системные разделы
            if dev.startswith("/dev/loop") or dev.startswith("/dev/ram"):
                continue  # циклические и RAM-устройства
            is_removable = (
                mount.startswith("/media/")
                or mount.startswith("/run/media/")
                or mount.startswith("/mnt/")
                or dev.startswith("/dev/mmcblk")
                or dev.startswith("/dev/usb")
            )
            if is_removable:
                found[mount] = (mount, dev, fstype)
        return sorted(found.values())

    def _open_removable(self) -> None:
        """Переход → Съёмные носители...: диалог со списком носителей.

        Носители есть — двойной клик открывает выбранный в основном окне;
        носителей нет — сообщение об ошибке (по заданию).
        """
        devices = self._list_removable()
        self._removable_roots = {os.path.abspath(m) for m, _, _ in devices}
        if not devices:
            self._error(cfg.MSG_NO_REMOVABLE)
            return

        dlg = QDialog(self)
        dlg.setWindowTitle("Съёмные носители")
        dlg.resize(480, 260)
        lay = QVBoxLayout(dlg)
        lay.addWidget(
            QLabel(
                "Подключённые съёмные носители.\nДвойной клик — открыть в основном окне:"
            )
        )
        lw = QListWidget()
        lay.addWidget(lw, 1)
        btns = QDialogButtonBox(QDialogButtonBox.Close)
        btns.rejected.connect(dlg.reject)
        btns.clicked.connect(dlg.reject)
        lay.addWidget(btns)

        for mount, dev, fstype in devices:
            it = QListWidgetItem(
                self._icon_for(mount, True),
                f"{mount}\n{dev}  [{fstype}]",
            )
            it.setData(cfg.FILEMANAGER_ROLE_PATH, mount)
            lw.addItem(it)

        def _open_device(cur: QListWidgetItem) -> None:
            path = cur.data(cfg.FILEMANAGER_ROLE_PATH)
            if path and os.path.isdir(path):
                self.navigate(path)
                dlg.accept()

        lw.itemDoubleClicked.connect(_open_device)
        dlg.exec_()

    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            cfg.ABOUT_TEXT_FILEMANAGER,
        )

    def _show_hotkeys(self) -> None:
        try:
            try:
                from src.modules.__func__.shortcuts import DefaultShortcutRegistry
            except ImportError:
                from modules.__func__.shortcuts import DefaultShortcutRegistry

            reg = DefaultShortcutRegistry()
            text = reg.help_text()
        except Exception as e:
            text = f"Не удалось сформировать справку:\n{e}"
        QMessageBox.information(self, "Горячие клавиши", text)

    def _error(self, message: str) -> None:
        QMessageBox.critical(self, "Суперапп", message)

    def _info(self, message: str) -> None:
        QMessageBox.information(self, "Суперапп", message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Суперапп")
    os.makedirs(cfg.TRASH_PATH, exist_ok=True)
    win = filemanager_func()
    win.navigate(cfg.SUPERAPP_ROOT)
    win.show()
    sys.exit(app.exec_())
