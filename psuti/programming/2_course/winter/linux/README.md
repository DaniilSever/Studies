# Linux App (PyQt6)

## Структура

```
.
├── main.py              # точка входа
├── requirements.txt     # зависимости
├── resources/           # иконки, стили, .ui-файлы
└── src/
    ├── app.py           # создание QApplication
    ├── config.py        # настройки и пути
    └── ui/
        └── main_window.py
```

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate      # для fish: source .venv/bin/activate.fish
pip install -r requirements.txt
python main.py
```
