import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QPlainTextEdit
)
from PyQt6.QtGui import QIcon, QFont
from core.renamer import rename_file, preview_rename, undo_rename, batch_rename
THEMES = {
    "dark": """
        QWidget { background:#0d1117; color:#c9d1d9; }
        QLineEdit { background:#161b22; padding:6px; border-radius:6px; }
        QPushButton { background:#21262d; padding:8px; border-radius:6px; }
        QPushButton:hover { background:#30363d; }
    """,
    "light": """
        QWidget { background:#ffffff; color:#000000; }
        QLineEdit { background:#f0f0f0; padding:6px; }
        QPushButton { background:#e0e0e0; padding:8px; }
    """
}

icon_path = "./assets/imaginex64x64.png"


class ImaginexApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_theme = "dark"
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("Imaginex • Smart File Renamer")
        self.setFixedSize(420, 400)
        self.init_ui()
            

    def init_ui(self):
        main_layout = QVBoxLayout()
        header_layout = QHBoxLayout()
        main_layout.addLayout(header_layout)
        main_layout.setSpacing(10)

        

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_btn.setFixedSize(32, 32)
        self.theme_btn.setToolTip("Toggle theme")
        self.theme_btn.clicked.connect(self.toggle_theme)

        self.theme_btn.setStyleSheet("""
        QPushButton {
            border: none;
            border-radius: 16px;
            background-color: #21262d;
        }
        QPushButton:hover {
            background-color: #30363d;
        }
        """)

        #header_layout.addWidget(title)
        header_layout.addStretch()   # 🔥 THIS pushes button to right
        header_layout.addWidget(self.theme_btn)

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
        self.setStyleSheet(THEMES[self.current_theme])

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
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if files:
            self.selected_files = files
            if len(files)>1:
                    self.file_input.setText(f"{len(files)} files selected")
            else:
                    self.file_input.setText(f"{(files)}")
            self.log_to_terminal(f"{(files)}", "INFO")

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
            # 1. Validation
            base_name = self.name_input.text().strip()
            if not hasattr(self, 'selected_files') or not self.selected_files:
                raise ValueError("No files selected. Please browse and select files first.")
            if not base_name:
                raise ValueError("Please enter a base name for the batch rename.")

            # 2. Confirmation Dialog (From your reference)
            count = len(self.selected_files)
            reply = QMessageBox.question(
                self, "Confirm Batch Rename", 
                f"Are you sure you want to rename {count} files?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                self.log_to_terminal(f"Starting batch rename for {count} files...", "INFO")
                
                # 3. Execution
                # Assuming your core.renamer.batch_rename returns a list of new paths
                renamed_paths = batch_rename(self.selected_files, base_name)
                
                # 4. Success Logging & Feedback
                success_msg = f"Successfully renamed {len(renamed_paths)} files."
                self.log_to_terminal(success_msg, "SUCCESS")
                
                
                # Show Success Alert
                QMessageBox.information(self, "Success", success_msg)
                
                # Optional: Clear selection after success
                self.selected_files = []
                self.file_input.clear()

        except Exception as e:
            # Error handling for both terminal and popup
            error_msg = str(e)
            self.log_to_terminal(f"BATCH ERROR: {error_msg}", "ERROR")
            QMessageBox.critical(self, "Error", error_msg)

            

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
    
    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
            self.theme_btn.setText("☀")
        else:
            self.current_theme = "dark"
            self.theme_btn.setText("🌙")

        self.setStyleSheet(THEMES[self.current_theme])
        self.log_to_terminal(
            f"Theme switched to {self.current_theme.upper()}",
            "INFO"
        )



if __name__ == "__main__":
    from PyQt6.QtCore import Qt

    app = QApplication(sys.argv)
    window = ImaginexApp()
    window.show()
    sys.exit(app.exec())
