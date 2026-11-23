import os
import shlex
import signal
import subprocess
import sys
import time
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

_HERE = os.path.dirname(os.path.abspath(__file__))
_SRC = os.path.dirname(_HERE)  # .../src
_PKG_ROOT = os.path.dirname(_SRC)  # .../ (System)
for _p in (_PKG_ROOT, _SRC):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import src.settings as cfg


def _fmt(color: QColor) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(color)
    return f


# ======================= [class terminal_ui] ================================
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
      * встроенные команды — сами, прямыми системными вызовами
        (os.listdir / os.mkdir / os.rename / os.kill / чтение /proc/...):
        базовый набор (cd/pwd/ls/mkdir/rmdir/cp/mv/rm/clear/help/history/
        echo/exit) + вариант 5, нечётный (ps/kill — управление процессами;
        lsdev/mounts/ioports — устройства ввода/вывода);
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

        # --- файловые операции (сисколлы) ------------------------------------
        if name == "ls":
            self._cmd_ls(args)
            return
        if name == "mkdir":
            self._cmd_mkdir(args)
            return
        if name == "rmdir":
            self._cmd_rmdir(args)
            return
        if name == "cp":
            self._cmd_cp(args)
            return
        if name == "mv":
            self._cmd_mv(args)
            return
        if name == "rm":
            self._cmd_rm(args)
            return

        # --- вариант 5 (нечётный): управление процессами ----------------------
        if name == "ps":
            self._cmd_ps()
            return
        if name == "kill":
            self._cmd_kill(args)
            return

        # --- вариант 5 (нечётный): устройства ввода/вывода --------------------
        if name == "lsdev":
            self._cmd_lsdev()
            return
        if name == "mounts":
            self._cmd_mounts()
            return
        if name == "ioports":
            self._cmd_ioports()
            return

    # --- встроенные команды: файловые операции (системные вызовы) ------------
    def _cmd_ls(self, args: list[str]) -> None:
        """ls [ПУТЬ] — список файлов каталога (os.listdir + os.stat)."""
        out = self.console.append_output
        target = args[0] if args else self._cwd
        path = self._resolve_path(target)
        try:
            entries = os.listdir(path)  # getdents64
        except OSError as e:
            out(cfg.MSG_T_SYSCALL.format(cmd="ls", err=e) + "\n", kind="stderr")
            return
        # папки впереди файлов, каждая с пометкой типа и размером (stat)
        try:
            entries.sort(key=lambda n: (not os.path.isdir(os.path.join(path, n)), n))
        except OSError:
            entries.sort()
        for n in entries:
            full = os.path.join(path, n)
            try:
                st = os.stat(full)  # stat
                if os.path.isdir(full):
                    out("{name:<28} <DIR>\n".format(name=n))
                else:
                    out("{name:<28} {size:>10}\n".format(name=n, size=st.st_size))
            except OSError:
                # объект исчез между listdir и stat — просто имя
                out("{name}\n".format(name=n))

    def _cmd_mkdir(self, args: list[str]) -> None:
        """mkdir ПУТЬ... — создать каталог(и) (os.mkdir)."""
        out = self.console.append_output
        if not args:
            out(cfg.MSG_T_NOARGS.format(cmd="mkdir"), kind="stderr")
            return
        for target in args:
            path = self._resolve_path(target)
            try:
                os.mkdir(path)  # mkdir(2)
            except FileExistsError:
                out(cfg.MSG_T_EXISTS.format(cmd="mkdir", path=target), kind="stderr")
            except OSError as e:
                out(
                    cfg.MSG_T_CANTCREATE.format(cmd="mkdir", path=target, err=e) + "\n",
                    kind="stderr",
                )

    def _cmd_rmdir(self, args: list[str]) -> None:
        """rmdir ПУТЬ... — удалить пустой каталог (os.rmdir)."""
        out = self.console.append_output
        if not args:
            out(cfg.MSG_T_NOARGS.format(cmd="rmdir"), kind="stderr")
            return
        for target in args:
            path = self._resolve_path(target)
            try:
                os.rmdir(path)  # rmdir(2)
            except FileNotFoundError:
                out(cfg.MSG_T_NOENT.format(cmd="rmdir", path=target), kind="stderr")
            except OSError as e:
                out(
                    cfg.MSG_T_CANTDEL.format(cmd="rmdir", path=target, err=e) + "\n",
                    kind="stderr",
                )

    @staticmethod
    def _copy_recursive(src: str, dst: str) -> None:
        """Копирование файла/каталога сисколлами: open/read/write/mkdir."""
        if os.path.isdir(src):
            os.mkdir(dst)
            for entry in os.listdir(src):
                _src = os.path.join(src, entry)
                _dst = os.path.join(dst, entry)
                terminal_func._copy_recursive(_src, _dst)
        else:
            with open(src, "rb") as fsrc, open(dst, "xb") as fdst:
                while True:
                    chunk = fsrc.read(65536)  # read(2)
                    if not chunk:
                        break
                    fdst.write(chunk)  # write(2)

    def _cmd_cp(self, args: list[str]) -> None:
        """cp ИСТ ДСТ — копировать файл/каталог (open/read/write, -R)."""
        out = self.console.append_output
        if len(args) < 2:
            out(cfg.MSG_T_TWOARGS.format(cmd="cp"), kind="stderr")
            return
        src = self._resolve_path(args[0])
        dst = self._resolve_path(args[1])
        # несколько источников -> последний аргумент обязан быть каталогом
        if len(args) > 2:
            if not os.path.isdir(dst):
                out(
                    "{cmd}: {path}: назначение должно быть каталогом\n".format(
                        cmd="cp", path=args[-1]
                    ),
                    kind="stderr",
                )
                return
            pairs = [
                (
                    self._resolve_path(a),
                    os.path.join(dst, os.path.basename(a.rstrip("/"))),
                )
                for a in args[:-1]
            ]
        else:
            new_dst = (
                os.path.join(dst, os.path.basename(src.rstrip("/")))
                if os.path.isdir(dst)
                else dst
            )
            pairs = [(src, new_dst)]
        for s, d in pairs:
            if not os.path.exists(s):
                out(cfg.MSG_T_NOENT.format(cmd="cp", path=s), kind="stderr")
                continue
            if os.path.exists(d):
                out(cfg.MSG_T_EXISTS.format(cmd="cp", path=d), kind="stderr")
                continue
            try:
                self._copy_recursive(s, d)
            except OSError as e:
                out(
                    cfg.MSG_T_CANTCOPY.format(cmd="cp", src=s, dst=d, err=e) + "\n",
                    kind="stderr",
                )

    def _cmd_mv(self, args: list[str]) -> None:
        """mv ИСТ ДСТ — переместить/переименовать (os.rename)."""
        out = self.console.append_output
        if len(args) < 2:
            out(cfg.MSG_T_TWOARGS.format(cmd="mv"), kind="stderr")
            return
        src = self._resolve_path(args[0])
        dst = self._resolve_path(args[1])
        if os.path.isdir(dst):
            dst = os.path.join(dst, os.path.basename(src.rstrip("/")))
        if not os.path.exists(src):
            out(cfg.MSG_T_NOENT.format(cmd="mv", path=args[0]), kind="stderr")
            return
        try:
            os.rename(src, dst)  # rename(2)
        except OSError as e:
            out(
                cfg.MSG_T_CANTMOVE.format(cmd="mv", src=src, dst=dst, err=e) + "\n",
                kind="stderr",
            )

    def _cmd_rm(self, args: list[str]) -> None:
        """rm [-r] ПУТЬ... — удалить файл (unlink) или каталог (rmdir/-r)."""
        out = self.console.append_output
        recursive = False
        targets = list(args)
        if targets and targets[0] == "-r":
            recursive = True
            targets = targets[1:]
        if not targets:
            out(cfg.MSG_T_NOARGS.format(cmd="rm"), kind="stderr")
            return

        def _rmtree(path: str) -> None:
            # рекурсивное удаление: unlink для файлов, rmdir для каталогов
            if os.path.isdir(path):
                for entry in os.listdir(path):
                    _rmtree(os.path.join(path, entry))
                os.rmdir(path)
            else:
                os.unlink(path)  # unlink(2)

        for target in targets:
            path = self._resolve_path(target)
            if not os.path.lexists(path):
                out(cfg.MSG_T_NOENT.format(cmd="rm", path=target), kind="stderr")
                continue
            try:
                if os.path.isdir(path):
                    if not recursive:
                        try:
                            os.rmdir(path)  # сработает только если пуст
                        except OSError:
                            out(
                                cfg.MSG_T_DIRNONEMPTY.format(cmd="rm", path=target),
                                kind="stderr",
                            )
                            continue
                    else:
                        _rmtree(path)
                else:
                    os.unlink(path)
            except OSError as e:
                out(
                    cfg.MSG_T_CANTDEL.format(cmd="rm", path=target, err=e) + "\n",
                    kind="stderr",
                )

    # --- вариант 5 (нечётный): управление процессами (системные вызовы) ------
    def _cmd_ps(self) -> None:
        """ps — список процессов ОС (чтение /proc/[pid]/stat — read(2))."""
        out = self.console.append_output
        out(
            cfg.MSG_T_PS_HDR.format(
                pid="PID", user="USER", state="S", start="START", name="NAME"
            ),
            kind="info",
        )
        n = 0
        for pid in sorted(self._proc_pids()):
            row = self._proc_row(pid)
            if row is None:
                continue
            out(row)
            n += 1
        if n == 0:
            out(cfg.MSG_T_PS_EMPTY, kind="info")

    @staticmethod
    def _proc_pids() -> list[int]:
        try:
            return sorted(int(e) for e in os.listdir("/proc") if e.isdigit())
        except OSError:
            return []

    def _proc_row(self, pid: int) -> Optional[str]:
        """Строка таблицы ps для одного процесса (аналог _read_stat мониторинга)."""
        try:
            with open("/proc/{pid}/stat".format(pid=pid), "r") as f:
                data = f.read()
        except OSError:
            return None
        rp = data.rfind(")")
        if rp == -1:
            return None
        comm = data[data.find("(") + 1 : rp]
        rest = data[rp + 2 :].split()
        state = rest[0] if rest else "?"
        try:
            starttime = int(rest[19]) if len(rest) > 19 else 0
        except ValueError:
            starttime = 0
        user = "-"
        try:
            with open("/proc/{pid}/status".format(pid=pid), "r") as f:
                for line in f:
                    if line.startswith("Uid:"):
                        parts = line.split()
                        uid = int(parts[1]) if len(parts) > 1 else -1
                        if uid >= 0:
                            import pwd as _pwd

                            user = _pwd.getpwuid(uid).pw_name
                        break
        except (OSError, ValueError, KeyError):
            pass
        start = self._proc_start_str(starttime)
        return cfg.MSG_T_PS_HDR.format(
            pid=pid, user=user, state=state, start=start, name=comm
        )

    @staticmethod
    def _proc_start_str(starttime_ticks: int) -> str:
        if starttime_ticks <= 0:
            return "?"
        try:
            with open("/proc/uptime", "r") as f:
                uptime = float(f.read().split()[0])
            boot = time.time() - uptime
            from datetime import datetime

            return datetime.fromtimestamp(
                boot + starttime_ticks / os.sysconf(os.sysconf_names["SC_CLK_TCK"])
            ).strftime("%H:%M:%S")
        except (OSError, ValueError):
            return "?"

    def _cmd_kill(self, args: list[str]) -> None:
        """kill PID [СИГ] — отправить сигнал процессу (os.kill)."""
        out = self.console.append_output
        if not args:
            out(cfg.MSG_T_NOARGS.format(cmd="kill"), kind="stderr")
            return
        sig = signal.SIGTERM
        if len(args) > 1:
            try:
                sig = int(args[1])
            except ValueError:
                out(
                    "{cmd}: {sig}: неверный номер сигнала\n".format(
                        cmd="kill", sig=args[1]
                    ),
                    kind="stderr",
                )
                return
        try:
            pid = int(args[0])
        except ValueError:
            out(cfg.MSG_T_BADPID.format(pid=args[0]), kind="stderr")
            return
        try:
            os.kill(pid, sig)  # kill(2)
        except ProcessLookupError:
            out(cfg.MSG_T_KILLED_ESRCH.format(pid=pid), kind="stderr")
            return
        except PermissionError:
            out(cfg.MSG_T_NOPERM.format(pid=pid), kind="stderr")
            return
        except OSError as e:
            out(
                cfg.MSG_T_SYSCALL.format(cmd="kill", err=e) + "\n",
                kind="stderr",
            )
            return
        out(cfg.MSG_T_KILLED.format(sig=sig, pid=pid), kind="info")

    # --- вариант 5 (нечётный): устройства ввода/вывода (системные вызовы) ----
    def _cmd_lsdev(self) -> None:
        """lsdev — блочные/символьные устройства /dev (listdir/stat по /dev)."""
        out = self.console.append_output
        out("УСТРОЙСТВО      ТИП     MAJ:MIN\n", kind="info")
        try:
            entries = sorted(os.listdir("/dev"))  # getdents64 по /dev
        except OSError as e:
            out(cfg.MSG_T_SYSCALL.format(cmd="lsdev", err=e) + "\n", kind="stderr")
            return
        n = 0
        for name in entries:
            full = os.path.join("/dev", name)
            try:
                st = os.lstat(full)  # lstat: не следуем по symlink
            except OSError:
                continue
            mode = st.st_mode & 0o170000  # S_IFMT
            if mode == 0o060000:  # S_IFBLK — блочное
                kind = "block"
            elif mode == 0o020000:  # S_IFCHR — символьное
                kind = "char"
            else:
                continue
            out(
                "{name:<14}  {kind:<6}  {maj}:{min}\n".format(
                    name=name,
                    kind=kind,
                    maj=os.major(st.st_rdev),
                    min=os.minor(st.st_rdev),
                )
            )
            n += 1
        if n == 0:
            out("(устройств не найдено)\n", kind="info")

    def _cmd_mounts(self) -> None:
        """mounts — смонтированные ФС (чтение /proc/mounts — read(2))."""
        out = self.console.append_output
        try:
            with open("/proc/mounts", "r") as f:
                lines = f.readlines()
        except OSError as e:
            out(
                cfg.MSG_T_NOVENTRY.format(name="/proc/mounts", err=e) + "\n",
                kind="stderr",
            )
            return
        out("УСТРОЙСТВО      ТОЧКА МОНТИРОВАНИЯ      ТИП ФС\n", kind="info")
        for line in lines:
            parts = line.split()
            if len(parts) < 3:
                continue
            mount = parts[1].replace("\\040", " ").replace("\\011", "\t")
            out(
                "{dev:<14}  {mount:<22}  {fstype}\n".format(
                    dev=parts[0], mount=mount, fstype=parts[2]
                )
            )

    def _cmd_ioports(self) -> None:
        """ioports — карта портов ввода/вывода (чтение /proc/ioports)."""
        out = self.console.append_output
        try:
            with open("/proc/ioports", "r") as f:
                text = f.read()
        except OSError as e:
            out(
                cfg.MSG_T_NOVENTRY.format(name="/proc/ioports", err=e) + "\n",
                kind="stderr",
            )
            return
        if text.strip():
            out(text)
        else:
            out("(/proc/ioports пуст)\n", kind="info")

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
