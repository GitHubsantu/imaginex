import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton,
    QLineEdit, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QPlainTextEdit
)
from PyQt6.QtGui import QIcon, QFont
from core.renamer import rename_file, preview_rename, undo_rename, batch_rename
from core.image_exif import get_image_date
from core.visual_analysis import analyze_brightness, count_faces
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".tiff", ".bmp"}
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


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

icon_path = resource_path("assets/imaginex64x64.png")

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
    def is_mixed_file_types(self, files):
        has_image = False
        has_other = False

        for f in files:
            ext = Path(f).suffix.lower()
            if ext in IMAGE_EXTENSIONS:
                has_image = True
            else:
                has_other = True

        return has_image and has_other

    def select_file(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files")
        if not files:
            return

        self.selected_files = files

        # UI text
        if len(files) > 1:
            self.file_input.setText(f"{len(files)} files selected")
        else:
            self.file_input.setText(files[0])

        # 🔥 MIXED FILE TYPE CHECK (FIRST)
        if self.is_mixed_file_types(files):
            self.log_to_terminal(
                "Mixed file types detected → smart naming disabled",
                "WARN"
            )
            self.name_input.clear()
            self.preview_label.clear()
            return

        # =========================
        # 🔥 SINGLE FILE LOGIC
        # =========================
        if len(files) == 1:
            base_name = ""

            # 🔹 EXIF AUTO SUGGESTION
            year_month = get_image_date(files[0])
            if year_month:
                year, month = year_month
                base_name = f"Photo_{month}_{year}"
                self.log_to_terminal("EXIF found (Date Taken)", "SUCCESS")
            else:
                self.log_to_terminal(
                    "EXIF missing (no Date Taken found)",
                    "WARN"
                )

            # 🔹 VISUAL ANALYSIS
            try:
                brightness = analyze_brightness(files[0])
                faces = count_faces(files[0])

                if faces >= 3:
                    scene = "Group_Photo"
                elif faces == 1:
                    scene = "Portrait"
                else:
                    scene = "Photo"

                self.log_to_terminal(
                    f"Visual analysis → {brightness}, Faces: {faces}",
                    "INFO"
                )

                # Combine EXIF + visual result
                if base_name:
                    final_name = f"{scene}_{base_name.replace('Photo_', '')}"
                else:
                    final_name = scene

                self.name_input.setText(final_name)

            except Exception as e:
                self.log_to_terminal(
                    f"Visual analysis skipped: {e}",
                    "WARN"
                )
                if base_name:
                    self.name_input.setText(base_name)

        # =========================
        # 🔥 BATCH FILE LOGIC
        # =========================
        else:
            # Batch → EXIF from first file only
            year_month = get_image_date(files[0])
            if year_month:
                year, month = year_month
                base_name = f"Photo_{month}_{year}"
                self.name_input.setText(base_name)
                self.log_to_terminal(
                    "EXIF found (batch base name set)",
                    "INFO"
                )
            else:
                self.log_to_terminal(
                    "EXIF missing for batch (manual name required)",
                    "WARN"
                )

        # 🔥 PREVIEW ALWAYS AT END
        self.show_preview()

            
    def show_preview(self):
        try:
            if not hasattr(self, "selected_files") or not self.selected_files:
                return

            name = self.name_input.text().strip()
            if not name:
                self.preview_label.clear()
                return

            first_file = Path(self.selected_files[0])
            new_path = preview_rename(first_file, name)

            self.preview_label.setText(
                f"Preview: {first_file.name}  →  {new_path.name}"
            )

        except Exception as e:
            self.log_to_terminal(str(e), "ERROR")

    def rename_action(self):
        try:
            if not hasattr(self, "selected_files") or not self.selected_files:
                raise ValueError("No files selected")

            name_input = self.name_input.text().strip()
            if not name_input:
                raise ValueError("Please enter name")

            count = len(self.selected_files)

            if count == 1:
                # 🔹 SINGLE FILE
                new_path = rename_file(self.selected_files[0], name_input)
                self.log_to_terminal(f"Renamed: {new_path.name}", "SUCCESS")
                QMessageBox.information(self, "Success", f"Renamed to: {new_path.name}")

            else:
                # 🔹 BATCH FILES
                reply = QMessageBox.question(
                    self, "Confirm Batch Rename",
                    f"Rename {count} files?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )

                if reply != QMessageBox.StandardButton.Yes:
                    return

                renamed = batch_rename(self.selected_files, name_input)
                self.log_to_terminal(f"Batch renamed {len(renamed)} files", "SUCCESS")
                QMessageBox.information(
                    self, "Success",
                    f"Renamed {len(renamed)} files successfully"
                )

            # reset after success
            self.selected_files = []
            self.file_input.clear()
            self.name_input.clear()
            self.preview_label.clear()


        except Exception as e:
            self.log_to_terminal(str(e), "ERROR")
            QMessageBox.critical(self, "Error", str(e))

            

    def undo_action(self):
        try:
            count = undo_rename()
            self.log_to_terminal(f"Undo successful ({count} files)", "WARN")
            QMessageBox.information(self, "Undo", f"Restored {count} file(s)")
        except Exception as e:
            self.log_to_terminal(str(e), "ERROR")
            QMessageBox.information(self, "Undo", str(e))

    
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
