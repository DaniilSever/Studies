from __future__ import annotations

import os
import shlex
import subprocess
import sys
from typing import Optional

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import (
    QColor,
    QFont,
    QKeyEvent,
    QKeySequence,
    QTextCharFormat,
    QTextCursor,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QMainWindow,
    QMenuBar,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

import src.settings as cfg


def _fmt(color: QColor) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(color)
    return f


class _Console(QPlainTextEdit):
    """Консольный виджет (xterm-стиль).

    Общее поведение виджета: история защищена от правки, ввод только на
    последней строке, история команд (↑/↓), горячие клавиши. Реальные
    действия уходят сигналами.
    """

    command_submitted = pyqtSignal(str)
    interrupt_requested = pyqtSignal()
    eof_requested = pyqtSignal()
    completion_requested = pyqtSignal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._prompt: str = "$ "
        self._history: list[str] = []
        self._hist_idx: int = 0
        self._input_start: int = 0  # позиция начала ввода в документе
        self._busy: bool = False  # идёт выполнение — ввод заблокирован

        f = QFont(cfg.TERMINAL_FONT_FAMILY)
        f.setStyleHint(QFont.TypeWriter)
        f.setPointSize(cfg.TERMINAL_FONT_SIZE)
        self.setFont(f)
        self.setStyleSheet(
            "QPlainTextEdit {{ background-color: {bg}; color: {fg}; border: none; }}".format(
                bg=cfg.TERMINAL_COL_BG, fg=cfg.TERMINAL_COL_FG
            )
        )
        self.setCursorWidth(8)
        self.setMinimumSize(560, 280)
        self.setReadOnly(False)
        self.cursorPositionChanged.connect(self._clamp_cursor)

        self._append_prompt(initial=True)

    # --- публичный API для func ---------------------------------------------
    def set_prompt(self, prompt: str) -> None:
        self._prompt = prompt

    def append_output(self, text: str, *, kind: str = "stdout") -> None:
        color = QColor(
            {
                "stdout": cfg.TERMINAL_COL_STDOUT,
                "stderr": cfg.TERMINAL_COL_STDERR,
                "info": cfg.TERMINAL_COL_INFO,
            }.get(kind, cfg.TERMINAL_COL_STDOUT)
        )
        if not text.endswith("\n"):
            text += "\n"
        self._insert_text(text, color)

    def append_raw(self, text: str) -> None:
        self._insert_text(text, QColor(cfg.TERMINAL_COL_FG))

    def show_help(self, text: str) -> None:
        if not text.endswith("\n"):
            text += "\n"
        self._insert_text(text, QColor(cfg.TERMINAL_COL_HELP))

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.setReadOnly(busy)

    def clear_screen(self) -> None:
        cur_input = self._current_input()
        self.clear()
        self._append_prompt(initial=True)
        self._replace_current_input(cur_input)

    def new_prompt(self) -> None:
        """func вызывает после завершения команды — вернуть ввод."""
        self._append_prompt()
        self.set_busy(False)

    # --- внутреннее: рисование ---------------------------------------------
    def _append_prompt(self, *, initial: bool = False) -> None:
        if not initial:
            self._insert_text("\n", QColor(cfg.TERMINAL_COL_FG))
        self._insert_text(self._prompt, QColor(cfg.TERMINAL_COL_PROMPT))
        self._input_start = self.textCursor().position()

    def _insert_text(self, text: str, color: QColor) -> None:
        c = self.textCursor()
        c.movePosition(QTextCursor.End)
        c.insertText(text, _fmt(color))
        self.setTextCursor(c)

    def _current_input(self) -> str:
        return self.document().toPlainText()[self._input_start :]

    def _replace_current_input(self, text: str) -> None:
        c = self.textCursor()
        c.setPosition(self._input_start)
        c.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        c.removeSelectedText()
        c.insertText(text, _fmt(QColor(cfg.TERMINAL_COL_FG)))
        c.movePosition(QTextCursor.End)
        self.setTextCursor(c)

    def _clamp_cursor(self) -> None:
        c = self.textCursor()
        # не выходим за пределы документа (актуально сразу после clear())
        doc_len = self.document().characterCount()
        start = self._input_start
        if doc_len > 0:
            start = max(0, min(start, doc_len - 1))
        else:
            start = 0
        if c.position() < start:
            c.setPosition(start)
            self.setTextCursor(c)

    # --- клавиатура: общее поведение консоли --------------------------------
    def keyPressEvent(self, e: QKeyEvent) -> None:
        if self._busy:
            if e.key() == Qt.Key_C and (e.modifiers() & Qt.ControlModifier):
                self.interrupt_requested.emit()
            return

        self._clamp_cursor()
        key = e.key()
        mods = e.modifiers()

        if key == Qt.Key_C and (mods & Qt.ControlModifier):
            self._insert_text("^C\n", QColor(cfg.TERMINAL_COL_STDERR))
            self.interrupt_requested.emit()
            self._history_reset()
            self._append_prompt()
            return

        if key == Qt.Key_L and (mods & Qt.ControlModifier):
            self.clear_screen()
            return

        if key == Qt.Key_D and (mods & Qt.ControlModifier):
            if self._current_input() == "":
                self._insert_text("\n", QColor(cfg.TERMINAL_COL_FG))
                self.eof_requested.emit()
                return

        if key == Qt.Key_Tab:
            self.completion_requested.emit(self._current_input())
            return

        if key == Qt.Key_Up:
            self._history_back()
            return
        if key == Qt.Key_Down:
            self._history_forward()
            return

        if key == Qt.Key_Home:
            c = self.textCursor()
            c.setPosition(self._input_start)
            self.setTextCursor(c)
            return
        if key == Qt.Key_End:
            c = self.textCursor()
            c.movePosition(QTextCursor.End)
            self.setTextCursor(c)
            return

        if key in (Qt.Key_Return, Qt.Key_Enter):
            self._submit()
            return

        if key == Qt.Key_Backspace:
            if self.textCursor().position() <= self._input_start:
                return
            super().keyPressEvent(e)
            return

        if e.text() == "" or (mods & Qt.ControlModifier):
            if e.matches(QKeySequence.Copy) or e.matches(QKeySequence.Paste):
                super().keyPressEvent(e)
            return

        super().keyPressEvent(e)

    # --- история команд -----------------------------------------------------
    def _submit(self) -> None:
        cmd = self._current_input()
        c = self.textCursor()
        c.movePosition(QTextCursor.End)
        c.insertText("\n", _fmt(QColor(cfg.TERMINAL_COL_FG)))
        self.setTextCursor(c)
        if cmd.strip():
            self._history.append(cmd)
        self._history_reset()
        self.command_submitted.emit(cmd)

    def _history_back(self) -> None:
        if not self._history:
            return
        if self._hist_idx > 0:
            self._hist_idx -= 1
        else:
            self._hist_idx = 0
        self._replace_current_input(self._history[self._hist_idx])

    def _history_forward(self) -> None:
        if not self._history:
            return
        if self._hist_idx < len(self._history) - 1:
            self._hist_idx += 1
            self._replace_current_input(self._history[self._hist_idx])
        else:
            self._hist_idx = len(self._history)
            self._replace_current_input("")

    def _history_reset(self) -> None:
        self._hist_idx = len(self._history)

    # --- история для func (чтение) -----------------------------------------
    def command_history(self) -> list[str]:
        return list(self._history)


class terminal_ui(QMainWindow):
    """Окно терминала: меню + консоль. Без логики выполнения команд."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(cfg.TERMINAL_TITLE)
        self.resize(*cfg.TERMINAL_SIZE)

        self._actions: dict[str, QAction] = {}
        self._build_menu()
        self._build_central()

    # --- меню ----------------------------------------------------------------
    def _build_menu(self) -> None:
        mb: QMenuBar = self.menuBar()

        def act(name: str, text: str, shortcut: str = "", tip: str = "") -> QAction:
            a = QAction(text, self)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            if tip:
                a.setStatusTip(tip)
            self._actions[name] = a
            return a

        m_term = mb.addMenu("Терминал")
        m_term.addAction(act("clear", "Очистить", "Ctrl+L"))
        m_term.addAction(act("interrupt", "Прервать (Ctrl+C)", "Ctrl+C"))
        m_term.addSeparator()
        m_term.addAction(act("close", "Закрыть", "Ctrl+W"))

        m_help = mb.addMenu("Справка")
        m_help.addAction(act("help", "Справка по командам", "F1"))

    # --- центральная область ------------------------------------------------
    def _build_central(self) -> None:
        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(0, 0, 0, 0)

        self.console = _Console()
        lay.addWidget(self.console)
        self.setCentralWidget(central)

    # --- публичный API (проброс к консоли) ----------------------------------
    def set_prompt(self, prompt: str) -> None:
        self.console.set_prompt(prompt)

    def append_output(self, text: str, *, kind: str = "stdout") -> None:
        self.console.append_output(text, kind=kind)

    def show_help(self, text: str = cfg.HELP_TEXT) -> None:
        self.console.show_help(text)

    def clear_screen(self) -> None:
        self.console.clear_screen()

    def set_busy(self, busy: bool) -> None:
        self.console.set_busy(busy)

    def new_prompt(self) -> None:
        self.console.new_prompt()


class terminal_func(terminal_ui):
    """Логика терминала поверх UI.

    Подключает сигналы консоли к разбору и выполнению команд:
      * встроенные команды (cd/pwd/clear/help/history/echo/exit) — сами;
      * прочие — через «bash -c» с захватом stdout/stderr;
      * ведёт текущий рабочий каталог (старт — корень «Суперапп»);
      * рендерит приглашение с путём.
    """

    def __init__(
        self, parent: Optional[QWidget] = None, start_cwd: Optional[str] = None
    ) -> None:
        super().__init__(parent)
        self._cwd: str = os.path.abspath(start_cwd or cfg.SUPERAPP_ROOT)
        if not os.path.isdir(self._cwd):
            self._cwd = os.path.abspath(cfg.SUPERAPP_ROOT)

        self._wire_signals()
        self._initial_view()

    # --- первичный экран -----------------------------------------------------
    def _initial_view(self) -> None:
        # баннер сверху, затем приглашение
        self.console.clear()
        self.console.append_output(cfg.BANNER, kind="info")
        self._render_prompt()
        self.console.new_prompt()

    # --- сигналы UI -> логика ------------------------------------------------
    def _wire_signals(self) -> None:
        c = self.console
        c.command_submitted.connect(self._on_command)
        c.interrupt_requested.connect(self._on_interrupt)
        c.eof_requested.connect(self._on_eof)

        A = self._actions.__getitem__
        A("clear").triggered.connect(self.console.clear_screen)
        A("interrupt").triggered.connect(self._on_interrupt)
        A("close").triggered.connect(self.close)
        A("help").triggered.connect(lambda: self.console.show_help(cfg.HELP_TEXT))

    # --- приглашение ---------------------------------------------------------
    def _render_prompt(self) -> None:
        # короткий путь: корень «Суперапп» показываем как ~
        root = os.path.abspath(cfg.SUPERAPP_ROOT)
        cwd = self._cwd
        if cwd == root:
            short = "~"
        elif cwd.startswith(root + os.sep):
            short = "~" + cwd[len(root) :]
        else:
            short = cwd
        self.set_prompt(
            cfg.TERMINAL_PROMPT_TEMPLATE.format(
                user=cfg.TERMINAL_PROMPT_USER, host=cfg.TERMINAL_PROMPT_HOST, cwd=short
            )
        )

    def _on_command(self, cmd: str) -> None:
        line = cmd.strip()
        if not line:
            self._after_command_prompt()
            return

        try:
            tokens = shlex.split(line)
        except ValueError:
            tokens = line.split()
        if not tokens:
            self._after_command_prompt()
            return

        name = tokens[0]
        args = tokens[1:]

        if name in cfg.TERMINAL_BUILTIN_COMMANDS:
            self.console.set_busy(True)
            self._run_builtin(name, args)
        else:
            self._run_external(line)

        self._after_command_prompt()

    def _run_builtin(self, name: str, args: list[str]) -> None:
        out = self.console.append_output

        if name in ("exit", "quit"):
            out(cfg.MSG_EXIT, kind="info")
            QApplication.quit()
            return

        if name in ("help", "?"):
            self.console.show_help(cfg.HELP_TEXT)
            return

        if name == "clear":
            self.console.clear_screen()
            return

        if name == "pwd":
            out(self._cwd + "\n")
            return

        if name == "cd":
            target = args[0] if args else os.path.abspath(cfg.SUPERAPP_ROOT)
            new = self._resolve_path(target)
            if not os.path.exists(new):
                out(cfg.MSG_BAD_DIR.format(path=target), kind="stderr")
                return
            if not os.path.isdir(new):
                out(cfg.MSG_CD_NOTDIR.format(path=target), kind="stderr")
                return
            self._cwd = os.path.abspath(new)
            return

        if name == "echo":
            out(" ".join(args) + "\n")
            return

        if name == "history":
            hist = self.console.command_history()
            if not hist:
                out("(история пуста)\n", kind="info")
                return
            for i, h in enumerate(hist, 1):
                out("{i:>4}  {h}\n".format(i=i, h=h))
            return

    def _run_external(self, line: str) -> None:
        """Внешняя команда — через «bash -c» с захватом вывода."""
        self.console.set_busy(True)
        try:
            proc = subprocess.run(
                ["bash", "-c", line],
                cwd=self._cwd,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired:
            self.console.append_output(
                "(превышено время ожидания: 30 с)\n", kind="stderr"
            )
            return
        except FileNotFoundError:
            self.console.append_output("bash не найден в системе\n", kind="stderr")
            return
        except OSError as e:
            self.console.append_output("ошибка запуска: {}\n".format(e), kind="stderr")
            return

        if proc.stdout:
            self.console.append_output(proc.stdout, kind="stdout")
        if proc.stderr:
            self.console.append_output(proc.stderr, kind="stderr")
        if proc.returncode != 0 and not proc.stderr:
            self.console.append_output(
                "(код возврата: {})\n".format(proc.returncode), kind="info"
            )

    # --- путь ---------------------------------------------------------------
    def _resolve_path(self, target: str) -> str:
        # ~ -> корень «Суперапп»; ~/<x> -> корень/<x>
        root = os.path.abspath(cfg.SUPERAPP_ROOT)
        if target == "~":
            return root
        if target.startswith("~/"):
            target = os.path.join(root, target[2:])
        if os.path.isabs(target):
            return os.path.normpath(target)
        return os.path.normpath(os.path.join(self._cwd, target))

    # --- прерывание / EOF ----------------------------------------------------
    def _on_interrupt(self) -> None:
        # ^C уже напечатан консолью; просто вернуть приглашение
        self._after_command_prompt()

    def _on_eof(self) -> None:
        QApplication.quit()

    def _after_command_prompt(self) -> None:
        """После выполнения команды — новое приглашение."""
        self._render_prompt()
        self.console.new_prompt()


def main(argv: list[str]) -> int:
    """Точка входа: терминал как отдельный процесс.

    Запускается из filemanager (F4 / меню «Терминал») или напрямую:
        python .../src/modules/terminal.py
    """
    app = QApplication(argv)
    app.setApplicationName("Суперапп — Терминал")

    win = terminal_func(start_cwd=cfg.SUPERAPP_ROOT)
    win.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
