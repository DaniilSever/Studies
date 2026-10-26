from PyQt6.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    def __init__(self, _title, _version) -> None:
        super().__init__()
        self.title = _title
        self.version = _version
        self.setWindowTitle(_title)
        self.resize(800, 600)

        self._build_menu()
        self._build_central_widget()
        self.statusBar().showMessage("Готово")

    def _build_menu(self) -> None:
        file_menu = self.menuBar().addMenu("&Файл")
        file_menu.addAction("&Выход", self.close)

        help_menu = self.menuBar().addMenu("&Справка")
        help_menu.addAction("&О программе", self._show_about)

    def _build_central_widget(self) -> None:
        self.label = QLabel("Привет, PyQt!")
        self.button = QPushButton("Нажми меня")
        self.button.clicked.connect(self._on_button_clicked)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)
        layout.addStretch()

        central = QWidget()
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _on_button_clicked(self) -> None:
        self.label.setText("Кнопка нажата!")
        self.statusBar().showMessage("Кнопка нажата", 2000)

    def _show_about(self) -> None:
        QMessageBox.about(self, "О программе", f"{self.title} v{self.version}")
