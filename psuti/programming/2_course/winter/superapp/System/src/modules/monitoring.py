import json
import os
import pwd
import re
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from typing import Optional

from PyQt5.QtCore import Qt, QTimer, pyqtSignal
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

_HERE = os.path.dirname(os.path.abspath(__file__))  # .../src/modules
_SRC = os.path.dirname(_HERE)  # .../src
_PKG_ROOT = os.path.dirname(_SRC)  # .../ (System)
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
    gpu_window_requested = pyqtSignal()
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

    # --- меню ----------------------------------------------------------------
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
        m_mon.addAction(act("gpu", "Информация о видеокарте", "Ctrl+G"))
        m_mon.addAction(act("log", "Открыть лог-файл", "Ctrl+Shift+L"))
        m_mon.addSeparator()
        m_mon.addAction(act("exit", "Закрыть", "Ctrl+W"))

        m_help = mb.addMenu("Справка")
        m_help.addAction(act("about", "О мониторинге", "F1"))

    # --- центральная область ------------------------------------------------
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
            ("gpu", "Видеокарта"),
            ("log", "Лог-файл"),
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

    # --- публичный API для func ---------------------------------------------
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


# ====================== [class monitoring_func] =============================
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

        # --- GPU popup (FIFO) ---
        self._gpu_fifo: Optional[str] = None
        self._gpu_wfd: Optional[int] = None
        self._gpu_proc: Optional[subprocess.Popen] = None
        self._gpu_timer = QTimer(self)
        self._gpu_timer.setInterval(cfg.MONITORING_REFRESH_MS)
        self._gpu_timer.timeout.connect(self._gpu_push)

        self._wire_signals()
        self.set_running(False)

    # --- сигналы UI -> логика ------------------------------------------------
    def _wire_signals(self) -> None:
        A = self._actions.__getitem__
        A("start").triggered.connect(self.start)
        A("stop").triggered.connect(self.stop)
        A("refresh").triggered.connect(self._refresh)
        A("save_report").triggered.connect(self.save_report)
        A("gpu").triggered.connect(self.gpu_open_popup)
        A("log").triggered.connect(self.log_save)
        A("about").triggered.connect(
            lambda: QMessageBox.about(self, "О мониторинге", cfg.ABOUT_TEXT_MONITORING)
        )
        A("exit").triggered.connect(self.close)

    # ==================================================================
    #  Управление мониторингом
    # ==================================================================
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

    # --- регистрация процессов приложения (для app.py) ----------------------
    def register_app_pid(self, pid: int) -> None:
        self._app_pids.add(pid)

    def unregister_app_pid(self, pid: int) -> None:
        self._app_pids.discard(pid)

    # ==================================================================
    #  Чтение /proc
    # ==================================================================
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

    # --- низкоуровневое чтение /proc/[pid]/* --------------------------------
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

    # ==================================================================
    #  Отчёт (Задание 3): процессы, запущенные во время работы «Суперапп»
    # ==================================================================
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

    # ==================================================================
    #  Доп. функционал (п.4, item 5): информация о видеокарте
    #  Вывод — во всплывающем окне (popup.py) через FIFO (pipe, вар. 5).
    #  Обновление в реальном времени + сохранение в лог-файл.
    # ==================================================================
    def gpu_open_popup(self) -> None:
        """Открыть всплывающее окно с инфо о видеокарте (отдельный процесс)."""
        if self._gpu_proc is not None and self._gpu_proc.poll() is None:
            QMessageBox.information(self, "Видеокарта", "Окно информации уже открыто.")
            return
        # создаём именованный канал (вар. 5 — pipe)
        tmp = tempfile.mkdtemp(prefix="superapp_gpu_")
        fifo = os.path.join(tmp, "gpu.fifo")
        try:
            os.mkfifo(fifo)
        except OSError as e:
            QMessageBox.critical(self, "Видеокарта", cfg.MSG_POPUP_FAIL.format(err=e))
            return
        self._gpu_fifo = fifo

        # запускаем popup.py отдельным процессом
        try:
            self._gpu_proc = subprocess.Popen(
                [sys.executable, cfg.POPUP_SCRIPT, fifo],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as e:
            QMessageBox.critical(self, "Видеокарта", cfg.MSG_POPUP_FAIL.format(err=e))
            return
        # регистрируем PID popup как процесс приложения (чтобы мониторинг
        # его не показывал в таблице процессов)
        self.register_app_pid(self._gpu_proc.pid)

        # открываем FIFO на запись (блокирует до появления читателя)
        try:
            self._gpu_wfd = os.open(fifo, os.O_WRONLY)
        except OSError as e:
            QMessageBox.critical(self, "Видеокарта", cfg.MSG_POPUP_FAIL.format(err=e))
            self._gpu_cleanup()
            return

        # первая отправка + запуск периодического обновления
        self._gpu_push()
        self._gpu_timer.start()
        self.set_status(
            "Окно «Видеокарта» открыто (FIFO). Обновление в реальном времени."
        )

    def _gpu_push(self) -> None:
        """Отправить актуальную инфо о видеокарте в popup (newline-JSON)."""
        if self._gpu_wfd is None:
            return
        fields = self.gpu_collect()
        if not fields:
            fields = [{"label": "Ошибка", "value": cfg.MSG_GPU_UNAVAIL}]
        msg = {
            "type": "data",
            "title": "Информация о видеокарте (вар. 5)",
            "fields": fields,
        }
        data = (json.dumps(msg, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            os.write(self._gpu_wfd, data)
        except OSError:
            # popup закрылся / pipe сломан — останавливаем
            self._gpu_stop()

    def gpu_collect(self) -> list[dict]:
        """Собрать информацию о видеокарте (best-effort, несколько источников)."""
        fields: list[dict] = []

        # 1) lspci — модель и PCI ID
        model, pci_id = self._gpu_from_lspci()
        if model:
            fields.append({"label": "Модель", "value": model})
        if pci_id:
            fields.append({"label": "PCI ID", "value": pci_id})

        # 2) драйвер NVIDIA + версия
        drv = self._read_nvidia_version()
        if drv:
            fields.append({"label": "Драйвер", "value": drv})

        # 3) nvidia-smi — загрузка/память/температура (real-time)
        fields.extend(self._gpu_from_nvidia_smi())

        # 4) метка времени — индикатор реального обновления
        fields.append(
            {"label": "Обновлено", "value": datetime.now().strftime("%H:%M:%S")}
        )

        return fields

    # --- источники данных GPU ------------------------------------------------
    def _gpu_from_lspci(self) -> tuple[str, str]:
        try:
            proc = subprocess.run(
                ["lspci", "-nn"], capture_output=True, text=True, timeout=5
            )
        except (OSError, subprocess.TimeoutExpired):
            return "", ""
        model, pci_id = "", ""
        for line in proc.stdout.splitlines():
            if re.search(
                r"\b(VGA compatible controller|3D controller|Display controller)\b",
                line,
            ):
                # "..." [1234:5678]
                m = re.search(r"\[([0-9a-fA-F]{4}:[0-9a-fA-F]{4})\]\s*(.*)$", line)
                if m:
                    pci_id = m.group(1)
                # текст модели — всё после ':'
                if ":" in line:
                    model = (
                        line.split(":", 2)[2].strip() if line.count(":") >= 2 else ""
                    )
                if model:
                    # убираем квадратные скобки с id из модели, если остались
                    model = re.sub(
                        r"\s*\[[0-9a-fA-F]{4}:[0-9a-fA-F]{4}\]", "", model
                    ).strip()
                break
        return model, pci_id

    @staticmethod
    def _read_nvidia_version() -> str:
        path = "/proc/driver/nvidia/version"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    first = f.readline().strip()
                return first
            except OSError:
                pass
        return ""

    @staticmethod
    def _gpu_from_nvidia_smi() -> list[dict]:
        try:
            proc = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=memory.total,memory.used,memory.free,utilization.gpu,temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            return []
        if proc.returncode != 0 or not proc.stdout.strip():
            return []
        parts = [p.strip() for p in proc.stdout.strip().split(",")]
        labels = [
            "Память всего, МБ",
            "Память занято, МБ",
            "Память свободно, МБ",
            "Загрузка GPU, %",
            "Температура, °C",
        ]
        out = []
        for label, val in zip(labels, parts):
            out.append({"label": label, "value": val})
        return out

    # --- остановка GPU popup -------------------------------------------------
    def _gpu_stop(self) -> None:
        if self._gpu_wfd is not None:
            try:
                os.write(
                    self._gpu_wfd,
                    (json.dumps({"type": "close"}) + "\n").encode("utf-8"),
                )
            except OSError:
                pass
        self._gpu_timer.stop()
        self._gpu_cleanup()

    def _gpu_cleanup(self) -> None:
        if self._gpu_wfd is not None:
            try:
                os.close(self._gpu_wfd)
            except OSError:
                pass
            self._gpu_wfd = None
        if self._gpu_proc is not None:
            try:
                self._gpu_proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._gpu_proc.terminate()
            if self._gpu_proc.pid in self._app_pids:
                self.unregister_app_pid(self._gpu_proc.pid)
            self._gpu_proc = None
        if self._gpu_fifo and os.path.exists(self._gpu_fifo):
            try:
                os.unlink(self._gpu_fifo)
                os.rmdir(os.path.dirname(self._gpu_fifo))
            except OSError:
                pass
            self._gpu_fifo = None

    # ==================================================================
    #  Лог-файл (Задание 4: возможность сохранения полученных данных)
    # ==================================================================
    def log_save(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить лог (видеокарта)",
            os.path.join(
                cfg.APP_ROOT,
                "gpu_log_{}.txt".format(datetime.now().strftime("%Y%m%d_%H%M%S")),
            ),
            "Текстовые файлы (*.txt);;Все файлы (*)",
        )
        if not path:
            return
        fields = self.gpu_collect()
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("Лог «Суперапп» — информация о видеокарте\n")
                f.write(
                    "Время: {}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                )
                f.write("----------------------------------------\n")
                if not fields:
                    f.write(cfg.MSG_GPU_UNAVAIL + "\n")
                else:
                    for fld in fields:
                        f.write("{}: {}\n".format(fld["label"], fld["value"]))
        except OSError as e:
            QMessageBox.critical(self, "Лог-файл", cfg.MSG_LOG_FAIL.format(err=e))
            return
        QMessageBox.information(self, "Лог-файл", cfg.MSG_LOG_SAVED.format(path=path))

    # ==================================================================
    #  Завершение
    # ==================================================================
    def closeEvent(self, event) -> None:
        self._gpu_stop()
        self._timer.stop()
        super().closeEvent(event)


# ============================ [def main] =====================================
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
