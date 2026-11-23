import json
import os
import pwd
import socket
import subprocess
import sys
import time
from datetime import datetime
from typing import Optional

from PyQt5.QtCore import QSocketNotifier, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
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


class monitoring_ui(QMainWindow):
    """UI: меню + таблица процессов + панель кнопок + статус.

    Без логики чтения /proc и запуска процессов. Действия выражены
    сигналами *_requested; логика — в monitoring_func.
    """

    start_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    refresh_requested = pyqtSignal()
    save_report_requested = pyqtSignal()
    hostname_window_requested = pyqtSignal()
    log_open_requested = pyqtSignal()
    about_requested = pyqtSignal()
    exit_requested = pyqtSignal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(cfg.MONITORING_TITLE)
        self.resize(*cfg.MONITORING_SIZE)

        self._actions: dict[str, QAction] = {}
        self._build_menu()
        self._build_central()

    # --- меню ---
    def _build_menu(self) -> None:
        mb: QMenuBar = self.menuBar()

        def act(name: str, text: str, shortcut: str = "") -> QAction:
            a = QAction(text, self)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            self._actions[name] = a
            return a

        m_mon = mb.addMenu("Мониторинг")
        m_mon.addAction(act("start", "Запустить мониторинг", "Ctrl+M"))
        m_mon.addAction(act("stop", "Остановить мониторинг"))
        m_mon.addAction(act("refresh", "Обновить", "F5"))
        m_mon.addSeparator()
        m_mon.addAction(act("save_report", "Сохранить отчёт...", "Ctrl+S"))
        m_mon.addAction(act("hostname", "Имя компьютера", "Ctrl+G"))
        m_mon.addAction(act("log", "Сохранить журнал ФМ...", "Ctrl+Shift+L"))
        m_mon.addAction(act("hostname_log", "Сохранить лог компьютера..."))
        m_mon.addSeparator()
        m_mon.addAction(act("exit", "Закрыть", "Ctrl+W"))

        m_help = mb.addMenu("Справка")
        m_help.addAction(act("about", "О мониторинге", "F1"))

    # --- центральная область ---
    def _build_central(self) -> None:
        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(8, 8, 8, 8)
        lay.setSpacing(8)

        # панель кнопок
        bar = QHBoxLayout()
        A = self._actions.__getitem__
        for key, label in (
            ("start", "Запустить"),
            ("stop", "Остановить"),
            ("refresh", "Обновить"),
            ("save_report", "Сохранить отчёт"),
            ("hostname", "Имя компьютера"),
            ("log", "Журнал ФМ"),
        ):
            btn = QPushButton(label)
            btn.clicked.connect(A(key).trigger)
            bar.addWidget(btn)
        bar.addStretch(1)
        lay.addLayout(bar)

        # таблица процессов
        self.table = QTableWidget(0, len(cfg.MONITORING_COLUMNS))
        self.table.setHorizontalHeaderLabels(cfg.MONITORING_COLUMNS)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        hdr = self.table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(1, QHeaderView.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        lay.addWidget(self.table, 1)

        # статус
        self.status = QLabel("Мониторинг остановлен")
        lay.addWidget(self.status)

        self.setCentralWidget(central)

    # --- публичный API для func ---
    def set_rows(self, rows: list[tuple]) -> None:
        """rows: список кортежей (pid, name, user, start, state)."""
        self.table.setRowCount(0)
        for r in rows:
            self.table.insertRow(self.table.rowCount())
            for col, val in enumerate(r):
                it = QTableWidgetItem(str(val))
                if col == 0:
                    it.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.table.setItem(self.table.rowCount() - 1, col, it)

    def set_status(self, text: str) -> None:
        self.status.setText(text)

    def set_running(self, running: bool) -> None:
        A = self._actions.__getitem__
        A("start").setEnabled(not running)
        A("stop").setEnabled(running)


class monitoring_func(monitoring_ui):
    """Логика мониторинга поверх UI.

    Источник данных — псевдофайловая система /proc (Linux). Никаких внешних
    команд для перечисления процессов: прямое чтение /proc/[pid]/stat,
    /proc/[pid]/cmdline, /proc/[pid]/status — это системные вызовы read()
    над procfs.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._timer = QTimer(self)
        self._timer.setInterval(cfg.MONITORING_REFRESH_MS)
        self._timer.timeout.connect(self._refresh)

        # множество PID, которые приложение запустило само (terminal/popup/...)
        self._app_pids: set[int] = set()
        # базовый снимок PID на старте мониторинга
        self._baseline_pids: set[int] = set()
        # процессы, появившиеся во время работы монитора (для отчёта):
        # {pid: (name, start_time_str)}
        self._session_started: dict[int, tuple[str, str]] = {}

        # --- hostname popup (сокет, вар. 1) ---
        self._srv_sock: Optional[socket.socket] = None
        self._srv_port: Optional[int] = None
        self._client_sock: Optional[socket.socket] = None
        self._srv_notifier = None  # QSocketNotifier на listening-сокет
        self._cli_notifier = None  # QSocketNotifier на клиентский сокет
        self._hostname_proc: Optional[subprocess.Popen] = None
        self._hostname_timer = QTimer(self)
        self._hostname_timer.setInterval(cfg.MONITORING_REFRESH_MS)
        self._hostname_timer.timeout.connect(self._hostname_push)

        self._wire_signals()
        self.set_running(False)

    # --- сигналы UI -> логика ---
    def _wire_signals(self) -> None:
        A = self._actions.__getitem__
        A("start").triggered.connect(self.start)
        A("stop").triggered.connect(self.stop)
        A("refresh").triggered.connect(self._refresh)
        A("save_report").triggered.connect(self.save_report)
        A("hostname").triggered.connect(self.hostname_open_popup)
        A("log").triggered.connect(self.journal_save)
        A("hostname_log").triggered.connect(self.log_save)
        A("about").triggered.connect(
            lambda: QMessageBox.about(self, "О мониторинге", cfg.ABOUT_TEXT_MONITORING)
        )
        A("exit").triggered.connect(self.close)

    def start(self) -> None:
        self._baseline_pids = self._enumerate_pids()
        self._session_started.clear()
        self._refresh()
        self._timer.start()
        self.set_running(True)
        self.set_status(
            f"Мониторинг запущен. Обновление каждые {cfg.MONITORING_REFRESH_MS} мс."
        )

    def stop(self) -> None:
        self._timer.stop()
        self.set_running(False)
        self.set_status("Мониторинг остановлен")

    # --- регистрация процессов приложения (для app.py) ---
    def register_app_pid(self, pid: int) -> None:
        self._app_pids.add(pid)

    def unregister_app_pid(self, pid: int) -> None:
        self._app_pids.discard(pid)

    def _refresh(self) -> None:
        rows, new_pids = self._collect_processes()
        self.set_rows(rows)
        for pid in new_pids:
            info = self._process_info(pid)
            if info is not None:
                self._session_started[pid] = (info["name"], info["start"])
        self.set_status(
            f"Процессов: {len(rows)}  |  новых за сессию: "
            f"{len(self._session_started)}  |  обновлено: "
            f"{datetime.now().strftime('%H:%M:%S')}"
        )

    def _enumerate_pids(self) -> set[int]:
        pids = set()
        try:
            for entry in os.listdir(cfg.MONITORING_PROC_ROOT):
                if entry.isdigit():
                    pids.add(int(entry))
        except OSError:
            pass
        return pids

    def _collect_processes(self) -> tuple[list[tuple], list[int]]:
        """Собрать строки таблицы. Возвращает (rows, new_pids_since_baseline)."""
        rows: list[tuple] = []
        new_pids: list[int] = []
        for pid in sorted(self._enumerate_pids()):
            if self._is_app_process(pid):
                continue
            info = self._process_info(pid)
            if info is None:
                continue
            rows.append((pid, info["name"], info["user"], info["start"], info["state"]))
            if pid not in self._baseline_pids:
                new_pids.append(pid)
        return rows, new_pids

    def _is_app_process(self, pid: int) -> bool:
        """Исключить процессы, запущенные из приложения (вар. 5, п.2)."""
        if pid in self._app_pids:
            return True
        cmdline = self._read_cmdline(pid)
        if not cmdline:
            return False
        joined = " ".join(cmdline)
        return any(script in joined for script in cfg.MONITORING_APP_SCRIPT_NAMES)

    def _process_info(self, pid: int) -> Optional[dict]:
        stat = self._read_stat(pid)
        if stat is None:
            return None
        name = stat["comm"]
        # полное имя из cmdline, если есть
        cmdline = self._read_cmdline(pid)
        if cmdline and cmdline[0]:
            name = os.path.basename(cmdline[0]) or name
        user = self._uid_to_user(stat["uid"])
        start = self._start_time_str(stat["starttime"])
        return {"name": name, "user": user, "start": start, "state": stat["state"]}

    # --- низкоуровневое чтение /proc/[pid]/* ---
    def _read_stat(self, pid: int) -> Optional[dict]:
        path = f"{cfg.MONITORING_PROC_ROOT}/{pid}/stat"
        try:
            with open(path, "r") as f:
                data = f.read()
        except OSError:
            return None
        # comm в скобках может содержать пробелы — разбор вручную
        rp = data.rfind(")")
        if rp == -1:
            return None
        comm = data[data.find("(") + 1 : rp]
        rest = data[rp + 2 :].split()
        # rest[0] = state (поле 3), rest[19] = starttime (поле 22)
        state = rest[0] if len(rest) > 0 else "?"
        try:
            starttime = int(rest[19]) if len(rest) > 19 else 0
        except ValueError:
            starttime = 0
        uid = self._read_uid(pid)
        return {"comm": comm, "state": state, "starttime": starttime, "uid": uid}

    def _read_uid(self, pid: int) -> int:
        path = f"{cfg.MONITORING_PROC_ROOT}/{pid}/status"
        try:
            with open(path, "r") as f:
                for line in f:
                    if line.startswith("Uid:"):
                        parts = line.split()
                        return int(parts[1]) if len(parts) > 1 else -1
        except OSError:
            pass
        return -1

    def _read_cmdline(self, pid: int) -> list[str]:
        path = f"{cfg.MONITORING_PROC_ROOT}/{pid}/cmdline"
        try:
            with open(path, "rb") as f:
                raw = f.read()
        except OSError:
            return []
        if not raw:
            return []
        return [p.decode("utf-8", "replace") for p in raw.split(b"\x00") if p]

    @staticmethod
    def _uid_to_user(uid: int) -> str:
        if uid < 0:
            return "-"
        try:
            return pwd.getpwuid(uid).pw_name
        except KeyError:
            return str(uid)

    @staticmethod
    def _boot_epoch() -> float:
        try:
            with open("/proc/uptime", "r") as f:
                uptime = float(f.read().split()[0])
        except OSError:
            return time.time()
        return time.time() - uptime

    def _start_time_str(self, starttime_ticks: int) -> str:
        if starttime_ticks <= 0:
            return "?"
        start_epoch = self._boot_epoch() + starttime_ticks / cfg.MONITORING_CLK_TCK
        return datetime.fromtimestamp(start_epoch).strftime("%H:%M:%S")

    def save_report(self) -> None:
        if not self._session_started:
            QMessageBox.information(self, "Отчёт", cfg.MSG_NO_REPORT)
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить отчёт",
            os.path.join(
                cfg.APP_ROOT,
                "report_{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
            ),
            "Текстовые файлы (*.txt);;Все файлы (*)",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(
                    cfg.REPORT_HEADER.format(
                        ts=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        n=len(self._session_started),
                    )
                )
                for name, start in self._session_started.values():
                    f.write(cfg.REPORT_LINE.format(name=name, start=start))
        except OSError as e:
            QMessageBox.critical(self, "Отчёт", cfg.MSG_REPORT_FAIL.format(err=e))
            return
        QMessageBox.information(
            self,
            "Отчёт",
            cfg.MSG_REPORT_SAVED.format(path=path, n=len(self._session_started)),
        )

    def hostname_open_popup(self) -> None:
        """Открыть всплывающее окно с именем компьютера (отдельный процесс)."""
        if self._hostname_proc is not None and self._hostname_proc.poll() is None:
            QMessageBox.information(
                self, "Имя компьютера", "Окно информации уже открыто."
            )
            return

        # поднимаем серверный сокет (вар. 1 — socket)
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((cfg.POPUP_HOST, 0))  # 0 — свободный порт от ОС
            srv.listen(1)
            srv.setblocking(False)
        except OSError as e:
            QMessageBox.critical(
                self, "Имя компьютера", cfg.MSG_POPUP_FAIL.format(err=e)
            )
            return
        port = srv.getsockname()[1]
        self._srv_sock = srv
        self._srv_port = port

        # запускаем popup.py отдельным процессом (клиент сокета)
        try:
            self._hostname_proc = subprocess.Popen(
                [sys.executable, cfg.POPUP_SCRIPT, cfg.POPUP_HOST, str(port)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            QMessageBox.critical(
                self, "Имя компьютера", cfg.MSG_POPUP_FAIL.format(err=e)
            )
            self._hostname_cleanup()
            return
        # регистрируем PID popup как процесс приложения (чтобы мониторинг
        # его не показывал в таблице процессов)
        self.register_app_pid(self._hostname_proc.pid)

        # следим за входящим соединением клиента (неблокирующе, по событию)
        self._srv_notifier = QSocketNotifier(srv.fileno(), QSocketNotifier.Read)
        self._srv_notifier.activated.connect(self._on_client_accepted)

        # первая отправка (сразу после connect) + периодическое обновление
        self._hostname_timer.start()
        self.set_status(
            f"Окно «Имя компьютера» открыто (сокет {cfg.POPUP_HOST}:{port}). "
            "Обновление в реальном времени."
        )

    def _on_client_accepted(self) -> None:
        """Клиент (popup) подключился — принимаем соединение."""
        assert self._srv_sock is not None
        self._srv_notifier.setEnabled(False)
        try:
            conn, _addr = self._srv_sock.accept()
        except BlockingIOError:
            self._srv_notifier.setEnabled(True)
            return
        except OSError:
            self._hostname_stop()
            return
        conn.setblocking(False)
        self._client_sock = conn
        self._cli_notifier = QSocketNotifier(conn.fileno(), QSocketNotifier.Read)
        self._cli_notifier.activated.connect(self._on_client_readable)

        # сразу отправляем текущие данные
        self._hostname_push()

    def _on_client_readable(self) -> None:
        """Клиент что-то прислал (обычно bye) или закрылся (EOF)."""
        assert self._client_sock is not None
        self._cli_notifier.setEnabled(False)
        try:
            chunk = self._client_sock.recv(4096)
        except BlockingIOError:
            self._cli_notifier.setEnabled(True)
            return
        except OSError:
            self._hostname_stop()
            return
        if not chunk:
            # EOF: popup закрылся сам -> останавливаем сервер и таймер
            self._hostname_stop()
            return
        # bye-сообщение от popup: пользователь закрыл окно сам
        data = chunk.decode("utf-8", "replace").strip()
        if '"close"' in data or '"bye"' in data:
            self._hostname_stop()
            return
        self._cli_notifier.setEnabled(True)

    def _hostname_push(self) -> None:
        """Отправить актуальную инфо в popup (newline-JSON по сокету)."""
        if self._client_sock is None:
            # клиент ещё не подключился — ждём accept
            return
        fields = self.hostname_collect()
        msg = {
            "type": "data",
            "title": "Имя компьютера (вар. 1)",
            "fields": fields,
        }
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            self._client_sock.sendall(data)
        except OSError:
            # popup закрылся / соединение сломано — останавливаем
            self._hostname_stop()

    def hostname_collect(self) -> list[dict]:
        """Собрать информацию об имени компьютера (несколько источников)."""
        fields: list[dict] = []

        # 1) имя хоста — стандартный gethostname (системный вызов)
        try:
            name = socket.gethostname()
        except OSError:
            name = ""
        if name:
            fields.append({"label": "Имя компьютера", "value": name})

        # 2) FQDN — полностью квалифицированное имя
        try:
            fqdn = socket.getfqdn()
        except OSError:
            fqdn = ""
        if fqdn and fqdn != name:
            fields.append({"label": "FQDN", "value": fqdn})

        # 3) /proc/sys/kernel/hostname — ядро Linux (чтение procfs)
        try:
            with open("/proc/sys/kernel/hostname", "r") as f:
                proc_name = f.read().strip()
            if proc_name and proc_name != name:
                fields.append({"label": "Имя (ядро, /proc)", "value": proc_name})
        except OSError:
            pass

        # 4) /etc/hostname — статическое имя (чтение файла)
        try:
            with open("/etc/hostname", "r") as f:
                etc_name = f.read().strip()
            if etc_name and etc_name != name:
                fields.append({"label": "Имя (/etc/hostname)", "value": etc_name})
        except OSError:
            pass

        # 5) домен из /etc/resolv.conf (best-effort)
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("domain "):
                        domain = line.split(None, 1)[1].strip()
                        if domain:
                            fields.append({"label": "Домен", "value": domain})
                        break
        except OSError:
            pass

        # 6) метка времени — индикатор реального обновления
        fields.append(
            {"label": "Обновлено", "value": datetime.now().strftime("%H:%M:%S")}
        )

        return fields

    # --- остановка hostname popup ---
    def _hostname_stop(self) -> None:
        if self._client_sock is not None:
            try:
                self._client_sock.sendall(
                    (json.dumps({"type": "close"}) + "\n").encode("utf-8")
                )
            except OSError:
                pass
        self._hostname_timer.stop()
        self._hostname_cleanup()

    def _hostname_cleanup(self) -> None:
        if self._cli_notifier is not None:
            self._cli_notifier.setEnabled(False)
            self._cli_notifier = None
        if self._client_sock is not None:
            try:
                self._client_sock.close()
            except OSError:
                pass
            self._client_sock = None
        if self._srv_notifier is not None:
            self._srv_notifier.setEnabled(False)
            self._srv_notifier = None
        if self._srv_sock is not None:
            try:
                self._srv_sock.close()
            except OSError:
                pass
            self._srv_sock = None
            self._srv_port = None
        if self._hostname_proc is not None:
            try:
                self._hostname_proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._hostname_proc.terminate()
            if self._hostname_proc.pid in self._app_pids:
                self.unregister_app_pid(self._hostname_proc.pid)
            self._hostname_proc = None

    def journal_save(self) -> None:
        """Сохранить журнал файлового менеджера (посещения и операции).

        Источник — fm_journal.log, который ведёт filemanager (куда
        заходил, что создавал/переименовывал/удалял). Здесь выбираем
        место копии и дописываем параметры посещений ФМ (сессия,
        длительность, число событий).
        """
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить журнал файлового менеджера",
            os.path.join(
                cfg.APP_ROOT,
                "fm_journal_{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
            ),
            "Текстовые файлы (*.txt);;Все файлы (*)",
        )
        if not path:
            return

        # читаем журнал, который ведёт файловый менеджер
        entries: list[str] = []
        try:
            with open(cfg.FM_JOURNAL_PATH, "r", encoding="utf-8") as f:
                entries = [line.rstrip("\n") for line in f if line.strip()]
        except FileNotFoundError:
            QMessageBox.information(
                self,
                "Журнал ФМ",
                "Журнал пуст: файловый менеджер ещё не запускался или событий не было.",
            )
            return
        except OSError as e:
            QMessageBox.critical(self, "Журнал ФМ", cfg.MSG_JOURNAL_FAIL.format(err=e))
            return

        # параметры посещений ФМ: сессия мониторинга и объём журнала
        visits = sum(1 for e in entries if "переход в каталог" in e)
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Журнал «Супрапп» — посещения и операции файлового менеджера\n")
                f.write(
                    "Сохранён: {}\n".format(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    )
                )
                f.write(
                    "Всего событий: {n}, посещений каталогов: {v}\n".format(
                        n=len(entries), v=visits
                    )
                )
                f.write("----------------------------------------\n")
                for e in entries:
                    f.write(e + "\n")
        except OSError as e:
            QMessageBox.critical(self, "Журнал ФМ", cfg.MSG_JOURNAL_FAIL.format(err=e))
            return
        QMessageBox.information(
            self,
            "Журнал ФМ",
            cfg.MSG_JOURNAL_SAVED.format(path=path, n=len(entries)),
        )

    def log_save(self) -> None:
        """Сохранить лог компьютера (снимок параметров: имя хоста и т.п.)."""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить лог (имя компьютера)",
            os.path.join(
                cfg.APP_ROOT,
                "hostname_log_{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
            ),
            "Текстовые файлы (*.txt);;Все файлы (*)",
        )
        if not path:
            return
        fields = self.hostname_collect()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Лог «Суперапп» — информация о компьютере (имя хоста)\n")
                f.write(
                    "Время: {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                f.write("----------------------------------------\n")
                if not fields:
                    f.write(cfg.MSG_HOSTNAME_UNAVAIL + "\n")
                else:
                    for fld in fields:
                        f.write("{}: {}\n".format(fld["label"], fld["value"]))
        except OSError as e:
            QMessageBox.critical(self, "Лог-файл", cfg.MSG_LOG_FAIL.format(err=e))
            return
        QMessageBox.information(self, "Лог-файл", cfg.MSG_LOG_SAVED.format(path=path))

    def closeEvent(self, event) -> None:
        self._hostname_stop()
        self._timer.stop()
        super().closeEvent(event)


def main(argv: list[str]) -> int:
    """Точка входа: мониторинг как отдельный процесс.

    Запускается из filemanager (Ctrl+M / меню «Мониторинг») или напрямую:
        python .../src/modules/monitoring.py
    """
    app = QApplication(argv)
    app.setApplicationName("Суперапп — Мониторинг")

    win = monitoring_func()
    win.show()
    # автозапуск мониторинга
    QTimer.singleShot(100, win.start)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
