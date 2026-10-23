"""Общие настройки приложения."""

from pathlib import Path

APP_NAME = "Linux App"
APP_VERSION = "0.1.0"

ROOT_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = ROOT_DIR / "resources"
