# Imaginex

Imaginex is an offline-first desktop tool that intelligently renames files
by understanding their content.

## Status
🚧 Under active development

## Day 1
- Manual file renaming (GUI)
## Day 2
- EXIF-based name suggestion (Date Taken)
- Visual analysis:
  - Brightness detection (day / night)
  - Face detection (portrait / group photos)

## Current Features
- Batch rename
- Filename cleaner
- Preview + Undo
- Dark / Light mode
- Activity terminal
### 🧠 Smart Image Naming
- EXIF-based name suggestion (Date Taken)
- Visual analysis:
  - Brightness detection (day / night)
  - Face detection (portrait / group photos)
- Human-friendly suggestions like:
```txt
IMG_0573.jpg → Portrait_Photo_Dec_2023.jpg
```

### 📂 Batch Renaming
- Batch rename with automatic numbering
- EXIF-based base name for photo batches
- Mixed file type detection (prevents incorrect smart renames)

### 🛡️ Safe by Design
- Preview before renaming
- Undo support (single & batch)
- No auto-rename behavior
- Offline only (no internet usage)

### 🎨 User Interface
- Dark / Light theme toggle
- Terminal-style activity log
- Clean and distraction-free layout
- Windows native executable (EXE)

### 🧹 Filename Tools
- Filename cleaner (extra spaces, junk patterns)
- Consistent naming format

---

## 🛠 Tech Stack
- Python 3
- PyQt6
- Pillow & EXIFRead
- OpenCV (visual analysis)
- PyInstaller (Windows EXE)

---
## 🔐 Privacy
- ✔ 100% offline
- ✔ No cloud uploads
- ✔ No tracking or telemetry

---

## 📄 License
MIT License

