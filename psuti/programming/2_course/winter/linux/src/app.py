"""Создание и запуск QApplication."""

from PyQt6.QtWidgets import QApplication

from src.config import APP_NAME, APP_VERSION
from src.ui.main_window import MainWindow


def run(argv: list[str]) -> int:
    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    window = MainWindow()
    window.show()

    return app.exec()
