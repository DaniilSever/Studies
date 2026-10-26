from PyQt6.QtWidgets import QApplication

from src.settings import APP_NAME, APP_VERSION
from src.ui.filemanager import MainWindow


def run(argv: list[str]) -> int:
    app = QApplication(argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(APP_VERSION)

    window = MainWindow(APP_NAME, APP_VERSION)
    window.show()

    return app.exec()
