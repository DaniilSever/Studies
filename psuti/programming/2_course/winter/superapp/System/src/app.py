import os
import sys

from PyQt5.QtWidgets import QApplication

import src.settings as cfg

from .modules.filemanager import filemanager_func


def _ensure_environment() -> None:
    """Минимальная среда «Суперапп»: Корзина (System уже есть по структуре)."""
    os.makedirs(cfg.TRASH_PATH, exist_ok=True)


def run(argv: list[str]) -> int:
    """Запуск «Суперапп»: подготовка среды + главное окно filemanager."""
    _ensure_environment()

    app = QApplication(argv)
    app.setApplicationName("Суперапп")
    app.setApplicationDisplayName("Суперапп")

    win = filemanager_func()
    start_path = cfg.SUPERAPP_ROOT
    # опциональный аргумент: стартовый каталог (например, для отладки)
    if len(argv) > 1 and os.path.isdir(argv[1]):
        start_path = argv[1]
    win.navigate(start_path)
    win.show()

    return app.exec_()
