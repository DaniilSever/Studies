import json
import os
import socket
import sys
from typing import Optional

from PyQt5.QtCore import QSocketNotifier, Qt, QTimer
from PyQt5.QtWidgets import (
    QApplication,
    QFormLayout,
    QFrame,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PopupWindow(QMainWindow):
    """Окно всплывающего процесса (вар. 1 — сокеты).

    Содержимое заполняется сообщениями главного окна, получаемыми по
    TCP-сокету (клиент). Главное окно закрывается/умирает -> соединение
    рвётся (EOF/ошибка чтения) -> окно закрывается: зависимость
    всплывающего окна от главного.
    """

    def __init__(self, host: str, port: int) -> None:
        super().__init__()
        self.host = host
        self.port = port
        self._sock: Optional[socket.socket] = None
        self._fd: Optional[int] = None
        self._notifier: Optional[QSocketNotifier] = None
        self._buf = bytearray()

        self.setWindowTitle("Суперапп — всплывающее окно")
        self.resize(420, 320)
        self.setMinimumSize(320, 200)

        central = QWidget()
        outer = QVBoxLayout(central)
        outer.setContentsMargins(12, 12, 12, 12)
        outer.setSpacing(10)

        self.title_label = QLabel("Ожидание данных...")
        self.title_label.setStyleSheet(
            "font-weight: bold; font-size: 13pt; color: #1f3a5f;"
        )
        self.title_label.setWordWrap(True)
        outer.addWidget(self.title_label)

        # разделитель
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #cccccc;")
        outer.addWidget(sep)

        # форма «метка: значение»
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        outer.addLayout(self.form, 1)

        self.empty_hint = QLabel("Данные ещё не получены.")
        self.empty_hint.setStyleSheet("color: #888;")
        outer.addWidget(self.empty_hint)

        # кнопка «Закрыть»
        self.close_btn = QPushButton("Закрыть")
        self.close_btn.clicked.connect(self._on_close_requested)
        outer.addWidget(self.close_btn, 0, Qt.AlignRight)

        self.setCentralWidget(central)

    def connect_to_server(self) -> bool:
        """Подключиться к серверному сокету главного окна.

        Неблокирующий connect с таймаутом: если главный процесс не поднял
        сервер за отведённое время — окно закрывается (зависимость).
        """
        try:
            sock = socket.create_connection((self.host, self.port), timeout=5)
        except OSError as e:
            sys.stderr.write(
                f"Не удалось подключиться к {self.host}:{self.port}: {e}\n"
            )
            return False
        sock.setblocking(False)
        self._sock = sock
        self._fd = sock.fileno()
        self._notifier = QSocketNotifier(self._fd, QSocketNotifier.Read)
        self._notifier.activated.connect(self._on_ready_read)
        return True

    def _on_ready_read(self) -> None:
        assert self._sock is not None
        # выключаем нотификатор на время обработки, чтобы избежать рекурсии
        self._notifier.setEnabled(False)
        try:
            while True:
                # после close/EOF сокет закрыт — выходим из цикла
                if self._sock is None:
                    return
                try:
                    chunk = self._sock.recv(4096)
                except BlockingIOError:
                    # данных больше нет в сокете — ждём следующего события
                    break
                except OSError:
                    # соединение сломано — главный процесс умер
                    self._on_disconnect()
                    return
                if not chunk:
                    # EOF: сервер закрыл соединение -> главного нет -> выходим
                    self._on_disconnect()
                    return
                self._buf.extend(chunk)
                self._drain_lines()
                # close-сообщение могло закрыть сокет и нотификатор
                if self._sock is None:
                    return
        finally:
            if self._notifier is not None:
                self._notifier.setEnabled(True)

    def _drain_lines(self) -> None:
        """Разбор полных строк (newline-delimited JSON) из буфера."""
        while b"\n" in self._buf:
            line, self._buf = self._buf.split(b"\n", 1)
            if not line.strip():
                continue
            try:
                msg = json.loads(line.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            self._handle_message(msg)

    def _handle_message(self, msg: dict) -> None:
        kind = msg.get("type")
        if kind == "data":
            self._apply_data(msg)
        elif kind == "close":
            self._on_close_requested()

    def _apply_data(self, msg: dict) -> None:
        title = msg.get("title") or "Всплывающее окно"
        self.setWindowTitle(f"Суперапп — {title}")
        self.title_label.setText(title)

        # очистить старые поля формы
        while self.form.rowCount():
            self.form.removeRow(0)
        self.empty_hint.setVisible(False)

        for field in msg.get("fields", []):
            label = str(field.get("label", ""))
            value = str(field.get("value", ""))
            value_lbl = QLabel(value)
            value_lbl.setWordWrap(True)
            value_lbl.setTextInteractionFlags(Qt.TextSelectableByMouse)
            self.form.addRow(label, value_lbl)

        if not msg.get("fields"):
            self.empty_hint.setText("Данные без полей.")
            self.empty_hint.setVisible(True)

    def _on_disconnect(self) -> None:
        """Главный процесс закрыл/потерял сокет — закрываемся (зависимость)."""
        self._cleanup()
        QApplication.quit()

    def _on_close_requested(self) -> None:
        if self._sock is not None:
            try:
                self._sock.sendall((json.dumps({"type": "bye"}) + "\n").encode("utf-8"))
            except OSError:
                pass
        self._cleanup()
        QApplication.quit()

    def _cleanup(self) -> None:
        if self._notifier is not None:
            self._notifier.setEnabled(False)
            self._notifier = None
        if self._sock is not None:
            try:
                self._sock.close()
            except OSError:
                pass
            self._sock = None
            self._fd = None

    def closeEvent(self, event) -> None:
        # крестик окна -> тоже закрываем процесс
        self._cleanup()
        super().closeEvent(event)
        QApplication.quit()


def main(argv: list[str]) -> int:
    # режим 1: --folder <path> — показать содержимое папки (Ctrl+двойной клик
    # в filemanager открывает новое окно). Режим 2 (по умолчанию): <host> <port>
    # — сокет-клиент для всплывающих окон с инфо (вар. 1: имя компьютера и т.п.).
    if len(argv) >= 3 and argv[1] == "--folder":
        folder = argv[2]
        if not os.path.isdir(folder):
            sys.stderr.write(f"Не папка: {folder}\n")
            return 2
        import signal as _sig

        _sig.signal(_sig.SIGPIPE, _sig.SIG_IGN)
        app = QApplication(sys.argv)
        win = FolderPopupWindow(folder)
        win.show()
        return app.exec_()

    if len(argv) < 3:
        sys.stderr.write(
            "Использование:\n"
            "  python popup.py <host> <port>     — сокет-режим (инфо, вар. 1)\n"
            "  python popup.py --folder <path>  — показать папку\n"
        )
        return 2

    host = argv[1]
    try:
        port = int(argv[2])
    except ValueError:
        sys.stderr.write(f"Неверный порт: {argv[2]}\n")
        return 2

    # не падать от SIGPIPE при отправке bye-сообщения серверу
    import signal as _sig

    _sig.signal(_sig.SIGPIPE, _sig.SIG_IGN)

    app = QApplication(sys.argv)
    win = PopupWindow(host, port)
    if not win.connect_to_server():
        return 3
    win.show()
    return app.exec_()


class FolderPopupWindow(QMainWindow):
    """Новое окно с содержимым папки (запускается отдельным процессом).

    Лёгкий просмотрщик: путь сверху, список элементов. Двойной клик по папке —
    переход внутри этого окна; по файлу — открыть средствами ОС. Окно
    независимо от главного (отдельный процесс), но закрывается пользователем.
    """

    def __init__(self, folder: str) -> None:
        super().__init__()
        self.setWindowTitle(f"Суперапп — {os.path.basename(folder) or folder}")
        self.resize(560, 400)

        central = QWidget()
        lay = QVBoxLayout(central)
        lay.setContentsMargins(6, 6, 6, 6)

        self.path_bar = QLineEdit(folder)
        lay.addWidget(self.path_bar)

        self.list = QPlainTextEdit()
        self.list.setReadOnly(True)
        lay.addWidget(self.list, 1)

        btn = QPushButton("Закрыть")
        btn.clicked.connect(QApplication.quit)
        lay.addWidget(btn, 0, Qt.AlignRight)

        self.setCentralWidget(central)
        self._show(folder)

    def _show(self, folder: str) -> None:
        self.path_bar.setText(folder)
        try:
            entries = sorted(os.listdir(folder))
        except OSError as e:
            self.list.setPlainText(f"Не удалось прочитать папку:\n{e}")
            return
        lines = [f"{folder}", f"({len(entries)} элементов)", ""]
        for name in entries:
            tag = "/" if os.path.isdir(os.path.join(folder, name)) else ""
            lines.append(f"{name}{tag}")
        self.list.setPlainText("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main(sys.argv))
