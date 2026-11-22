import json
import os
import sys
from typing import Optional

from PyQt5.QtCore import QSocketNotifier, Qt
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
    """Окно всплывающего процесса. Содержимое заполняется сообщениями из FIFO."""

    def __init__(self, fifo_path: str) -> None:
        super().__init__()
        self.fifo_path = fifo_path
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

    # ======================================================================
    #  Открытие FIFO
    # ======================================================================
    def open_pipe(self) -> None:
        """Открыть FIFO на чтение (неблокирующе). FIFO создаёт главный процесс."""
        # O_NONBLOCK: open не виснет, если писателя ещё нет
        fd = os.open(self.fifo_path, os.O_RDONLY | os.O_NONBLOCK)
        self._fd = fd
        self._notifier = QSocketNotifier(fd, QSocketNotifier.Read)
        self._notifier.activated.connect(self._on_ready_read)

    # ======================================================================
    #  Чтение из FIFO (неблокирующее, по событию)
    # ======================================================================
    def _on_ready_read(self) -> None:
        assert self._fd is not None
        # выключаем нотификатор на время обработки, чтобы избежать рекурсии
        self._notifier.setEnabled(False)
        try:
            while True:
                # после close/EOF fd закрывается — выходим из цикла
                if self._fd is None:
                    return
                try:
                    chunk = os.read(self._fd, 4096)
                except BlockingIOError:
                    # данных больше нет в FIFO — ждём следующего события
                    break
                except OSError:
                    # pipe сломан — главный процесс умер
                    self._on_eof()
                    return
                if not chunk:
                    # EOF: все писатели закрыли FIFO -> главного нет -> выходим
                    self._on_eof()
                    return
                self._buf.extend(chunk)
                self._drain_lines()
                # close-сообщение могло закрыть fd и нотификатор
                if self._fd is None:
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
                # битое сообщение игнорируем, но не падаем
                continue
            self._handle_message(msg)

    def _handle_message(self, msg: dict) -> None:
        kind = msg.get("type")
        if kind == "data":
            self._apply_data(msg)
        elif kind == "close":
            self._on_close_requested()
        # неизвестные типы молча игнорируем

    # ======================================================================
    #  Применение данных к окну
    # ======================================================================
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

    # ======================================================================
    #  Закрытие / EOF
    # ======================================================================
    def _on_eof(self) -> None:
        """Главный процесс закрыл/потерял FIFO — закрываемся (зависимость)."""
        self._cleanup()
        QApplication.quit()

    def _on_close_requested(self) -> None:
        self._cleanup()
        QApplication.quit()

    def _cleanup(self) -> None:
        if self._notifier is not None:
            self._notifier.setEnabled(False)
            self._notifier = None
        if self._fd is not None:
            try:
                os.close(self._fd)
            except OSError:
                pass
            self._fd = None

    def closeEvent(self, event) -> None:
        # крестик окна -> тоже закрываем процесс
        self._cleanup()
        super().closeEvent(event)
        QApplication.quit()


def main(argv: list[str]) -> int:
    # режим 1: --folder <path> — показать содержимое папки (Ctrl+двойной клик
    # в filemanager открывает новое окно). Режим 2 (по умолчанию): <fifo_path>
    # — FIFO-клиент для всплывающих окон с инфо (вар. 5: видеокарта и т.п.).
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

    if len(argv) < 2:
        sys.stderr.write(
            "Использование:\n"
            "  python popup.py <fifo_path>            — FIFO-режим (инфо)\n"
            "  python popup.py --folder <path>        — показать папку\n"
        )
        return 2

    fifo_path = argv[1]

    if not os.path.exists(fifo_path):
        sys.stderr.write(f"FIFO не существует: {fifo_path}\n")
        return 2

    # не падать от SIGPIPE (на случай записи обратно — здесь только чтение,
    # но для надёжности отдельного процесса игнорируем)
    import signal as _sig

    _sig.signal(_sig.SIGPIPE, _sig.SIG_IGN)

    app = QApplication(sys.argv)
    win = PopupWindow(fifo_path)
    win.open_pipe()
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
