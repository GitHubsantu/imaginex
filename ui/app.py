import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QPlainTextEdit
)
from PyQt6.QtGui import QIcon, QFont
from core.renamer import rename_file, preview_rename, undo_rename

icon_path = "./assets/imaginex64x64.png"


class ImaginexApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Imaginex • Smart File Renamer")
        self.setFixedSize(420, 320)
        self.init_ui()
            

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)

        title = QLabel("Imaginex")
        title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle = QLabel("Offline • Safe • Open Source")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color: gray;")

        # File selection
        self.file_input = QLineEdit()
        self.file_input.setReadOnly(True)
        self.file_input.setPlaceholderText("Select a file...")

        browse_btn = QPushButton("📂 Browse")
        browse_btn.clicked.connect(self.select_file)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_input)
        file_layout.addWidget(browse_btn)

        # New name input
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("New name (without extension)")
        self.name_input.textChanged.connect(self.show_preview)

        self.terminal = QPlainTextEdit()
        self.terminal.setMinimumHeight(110)
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #000000;
                    color: #00ff9c;
                    border: 2px solid #00ff9c;
                    border-radius: 6px;
                    padding: 8px;
                    font-family: Consolas, monospace;
                    font-size: 9pt;
                }

                QPlainTextEdit::selection {
                    background-color: #00ff9c;
                    color: black;
                }
                """)
        font = QFont("Segoe UI", 11) 
        self.terminal.setFont(font)

        # Preview label
        self.preview_label = QLabel("")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("color: #1e88e5;")

        # Buttons
        rename_btn = QPushButton("✍️ Confirm Rename")
        rename_btn.clicked.connect(self.rename_action)

        undo_btn = QPushButton("↩ Undo")
        undo_btn.clicked.connect(self.undo_action)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(rename_btn)
        btn_layout.addWidget(undo_btn)

        # Assemble layout
        main_layout.addWidget(title)
        main_layout.addWidget(subtitle)
        main_layout.addLayout(file_layout)
        main_layout.addWidget(self.name_input)
        main_layout.addWidget(QLabel("🖥 System Log"))
        main_layout.addWidget(self.terminal)
        main_layout.addWidget(self.preview_label)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

    def log_to_terminal(self, message, level="INFO"):
        colors = {
            "INFO": "#58a6ff",
            "SUCCESS": "#3fb950",
            "ERROR": "#f85149",
            "WARN": "#d29922"
        }
        color = colors.get(level, "#c9d1d9")
        self.terminal.appendHtml(
            f'<span style="color:{color}">root@user:~ {message}</span>'
        )
        self.terminal.verticalScrollBar().setValue(
            self.terminal.verticalScrollBar().maximum()
        )

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File")
        if file_path:
            self.file_input.setText(file_path)
            self.show_preview()

    def show_preview(self):
        try:
            path = self.file_input.text()
            name = self.name_input.text().strip()

            if path and name:
                new_path = preview_rename(path, name)
                self.log_to_terminal(f"Preview:\n{Path(path).name}  →  {new_path.name}", "INFO")
            else:
                self.log_to_terminal("")
        except Exception as e:
            error = str(e)
            self.log_to_terminal(f"Error: {error}", "ERROR")

    def rename_action(self):
        try:
            path = self.file_input.text()
            name = self.name_input.text().strip()

            if not path or not name:
                raise ValueError("Please select a file and enter a new name")
            
            reply = QMessageBox.question(None, "Confirm", "Do you want to Rename?", 
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                new_path = rename_file(path, name)
                self.log_to_terminal(f"File renamed to: {new_path.name}", "SUCCESS")
                QMessageBox.information(
                    self, "Success",
                    f"File renamed to: {new_path.name}"
                )

        except Exception as e:
            error = str(e)
            self.log_to_terminal(f"Error: {error}", "ERROR")
            QMessageBox.critical(self, "Error", error)
            

    def undo_action(self):
        self.log_to_terminal("You are trying to Undo.", "WARN")
        reply = QMessageBox.question(None, "Confirm", "Do you want to Undo?", 
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
                try:
                    old_path = undo_rename()
                    self.log_to_terminal(f"Undo successful:\n{old_path.name}", "WARN")
                except Exception as e:
                    error = str(e)
                    self.log_to_terminal(f"Error: {error}", "ERROR")
                    QMessageBox.information(self, "Undo", error)


if __name__ == "__main__":
    from PyQt6.QtCore import Qt

    app = QApplication(sys.argv)
    window = ImaginexApp()
    window.show()
    sys.exit(app.exec())
