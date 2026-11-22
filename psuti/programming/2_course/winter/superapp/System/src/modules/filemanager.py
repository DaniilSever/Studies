from __future__ import annotations

import os
import subprocess
import sys
from typing import Optional

from PyQt5.QtCore import QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileIconProvider,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QStyle,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

import src.settings as cfg


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
        self._icon_provider = QFileIconProvider()

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
            "open_terminal",
            "Открыть терминал",
            "F4",
            st.standardIcon(QStyle.SP_CommandLink),
        )
        act("exit", "Выход", "Ctrl+Q")

        # Правка
        act("cut", "Вырезать", "Ctrl+X")
        act("copy", "Копировать", "Ctrl+C")
        act("paste", "Вставить", "Ctrl+V")
        act("select_all", "Выделить всё", "Ctrl+A")

        # Вид
        act("refresh", "Обновить", "F5", st.standardIcon(QStyle.SP_BrowserReload))

        # Переход
        act("back", "Назад", "Alt+Left", st.standardIcon(QStyle.SP_ArrowLeft))
        act("forward", "Вперёд", "Alt+Right", st.standardIcon(QStyle.SP_ArrowRight))
        act("up", "Вверх", "Alt+Up", st.standardIcon(QStyle.SP_ArrowUp))

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
        m_file.addAction(A("open_terminal"))
        m_file.addSeparator()
        m_file.addAction(A("exit"))

        m_edit = mb.addMenu("Правка")
        m_edit.addAction(A("cut"))
        m_edit.addAction(A("copy"))
        m_edit.addAction(A("paste"))
        m_edit.addSeparator()
        m_edit.addAction(A("select_all"))

        m_view = mb.addMenu("Вид")
        m_view.addAction(A("refresh"))

        m_go = mb.addMenu("Переход")
        m_go.addAction(A("back"))
        m_go.addAction(A("forward"))
        m_go.addAction(A("up"))

        m_term = mb.addMenu("Терминал")
        m_term.addAction(A("open_terminal"))

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

        self.list = QListWidget()
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

    # --- вкл/выкл навигации (общее поведение UI) ---
    def update_nav_state(self, can_back: bool, can_forward: bool, can_up: bool) -> None:
        self._actions["back"].setEnabled(can_back)
        self._actions["forward"].setEnabled(can_forward)
        self._actions["up"].setEnabled(can_up)


# ==================== [class filemanager_func] ==============================
class filemanager_func(filemanager_ui):
    """Логика файлового менеджера поверх UI.

    Наследует UI, подключает сигналы к реальным действиям: чтение каталога,
    навигация, открытие папок/файлов, запуск popup.py и terminal.py,
    защита папки System.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # история навигации
        self._history: list[str] = []
        self._history_pos: int = -1

        self._wire_signals()
        self._update_nav()

    # --- подключение сигналов UI -> логика ----------------------------------
    def _wire_signals(self) -> None:
        A = self._actions.__getitem__

        A("back").triggered.connect(self._go_back)
        A("forward").triggered.connect(self._go_forward)
        A("up").triggered.connect(self._go_up)
        A("refresh").triggered.connect(self._reload)

        self.path_bar.returnPressed.connect(self._on_path_entered)

        self.list.itemDoubleClicked.connect(self._on_item_double_clicked)

        A("open_terminal").triggered.connect(self._open_terminal)
        A("exit").triggered.connect(self.close)

        A("about").triggered.connect(self._show_about)
        A("hotkeys").triggered.connect(self._show_hotkeys)

    # ==================================================================
    #  Навигация
    # ==================================================================
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
        cur = self.path_bar.text().strip()
        if not cur:
            return
        up = os.path.dirname(cur.rstrip("/")) or "/"
        # не выходим за пределы корня «Суперапп»
        if up == os.path.dirname(cfg.SUPERAPP_ROOT) and not cur.startswith(
            cfg.SUPERAPP_ROOT
        ):
            return
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

    # ==================================================================
    #  Заполнение плиток
    # ==================================================================
    def _populate(self, path: str) -> None:
        self.list.clear()
        try:
            entries = sorted(os.listdir(path))
        except OSError as e:
            self._error(cfg.MSG_OPEN_ERROR.format(name=path, err=e))
            return

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
        # системная иконка через QFileIconProvider (как в Thunar)
        from PyQt5.QtCore import QFileInfo

        return self._icon_provider.icon(QFileInfo(path))

    # ==================================================================
    #  Открытие элементов
    # ==================================================================
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

    # ==================================================================
    #  Справка / О программе
    # ==================================================================
    def _show_about(self) -> None:
        QMessageBox.about(
            self,
            "О программе",
            "Суперапп — файловый менеджер.\n"
            "Курсовая работа по ОСиО.\n"
            "Вариант 5 (каналы, процессы ОС, GPU).\n"
            "Язык: Python + PyQt5.\n"
            "Разработчик: 【ФИО, группа】",
        )

    def _show_hotkeys(self) -> None:
        try:
            from modules.__func__.shortcuts import DefaultShortcutRegistry

            reg = DefaultShortcutRegistry()
            text = reg.help_text()
        except Exception as e:
            text = f"Не удалось сформировать справку:\n{e}"
        QMessageBox.information(self, "Горячие клавиши", text)

    # ==================================================================
    #  Утилиты
    # ==================================================================
    def _error(self, message: str) -> None:
        QMessageBox.critical(self, "Суперапп", message)
