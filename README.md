# PyQt6 Python Notepad Application for UPC Project

A feature-rich notepad application built using **PyQt6**, offering text editing, file operations, printing, audio conversion, screenshot capture, and theme toggling capabilities.

---

## 📁 File Overview

- **File Name**: `UPC Notepad`
- **Purpose**: Implementation of a full-featured notepad application.
- **Technology Stack**: Python + PyQt6
- **Python Version** : 3.13
- **Main Class**: `MainWindow(QMainWindow)`
- **Libraries Used**:
  - `PyQt6.QtGui`, `PyQt6.QtWidgets`, `PyQt6.QtCore`
  - `PyQt6.QtPrintSupport`, `PyQt6.QtTextToSpeech`
  - `os`, `sys`, `json`, `datetime`, `shutil`, `gTTS`

---

## 🧱 Core Components

### 1. **UI Layout**
- Uses `QVBoxLayout` for vertical layout management.
- Central widget: `QPlainTextEdit` with monospaced font (`Courier New`).
- Toolbars:
  - **File Toolbar**: Open, Save, Save As, Print
  - **Edit Toolbar**: Undo, Redo, Copy, Paste, Cut, Clear, Select All, Remove, Date/Time Insertion, Screenshot, Theme Toggle
  - **Audio Toolbar**: Read Aloud, Stop Reading, Restart, Read Selected Text, Convert to Speech
- Status Bar for feedback messages.

### 2. **Menu System**
- Menus:
  - **File**: File operations (Open, Save, Save As, Print)
  - **Edit**: Editing functions (Undo, Redo, Copy, Paste, Cut, Clear, Select All, Remove, Insert Date/Time)
  - **Audio**: Audio-related actions (Read, Stop, Restart, Read Selection, Convert to Speech)

---

## 💡 Features Implemented

| Feature | Description |
|--------|-------------|
| **File Handling** | Open, Save, Save As, Print |
| **Text Editing** | Undo/Redo, Copy/Paste/Cut, Clear, Select All, Remove Selection |
| **Date/Time Insert** | Insert current date, time, or both at cursor position |
| **Screenshot Capture** | Take screen capture and save as image |
| **Theme Switching** | Light/Dark mode toggle with persistent config via JSON |
| **Text-to-Speech** | Built-in speech synthesis using `QTextToSpeech` and `gTTS` |
| **Audio Export** | Save synthesized speech as `.mp3` file |
| **Status Feedback** | Real-time status updates in status bar |

---

## ⚙️ Key Methods

### 🔹 File Operations
- `file_open()`: Opens a `.txt` file.
- `file_save()` / `file_saveas()`: Saves content to file.
- `_save_to_path(path)`: Internal save logic.
- `file_print()`: Prints document via system printer dialog.

### 🔹 Edit Functions
- `edit_toggle_wrap()`: Toggles line wrapping.
- `insert_date()`, `insert_time()`, `insert_date_time()`: Insert current timestamp.
- `remove_action()`: Removes selected text.
- `clear_action()`: Clears all text.

### 🔹 Screenshot
- `take_screenshot()`: Captures screen and allows saving.

### 🔹 Audio & TTS
- `read_aloud()`, `stop_reading()`, `restart_reading()`: Controls voice playback.
- `read_selected_text()`: Reads only selected text aloud.
- `convert_text_to_speech()`: Converts text to `.mp3` using gTTS.
- `audio_save()`: Saves generated audio file to disk.

### 🔹 Theme Management
- `load_theme()`, `save_theme(theme)`, `apply_theme(editor)`, `toggle_theme(editor)`: Handles light/dark switching and persistence.

---

## 🧾 Configuration

- **Config File**: `config.json` stores theme preference.
- **Screenshots Directory**: `./screenshots`
- **Icon**: Looks for `./icon/upc.png` for window icon.

---

## 🧪 Error Handling

- Uses `QMessageBox.critical` to display errors.
- Try-except blocks wrap all I/O operations (files, audio, screenshots).

---

## 🖥️ Entry Point

```python
if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setApplicationName("PyQt6-Notepad")
    window = MainWindow()
    window.showMaximized()
    if os.path.exists("./icon/upc.png"):
        window.setWindowIcon(QIcon("./icon/upc.png"))
    window.apply_theme(window.editor)
    sys.exit(app.exec())
---
## Installation
```commands
git clone ...

cd ...

chmod +x university_upc.py

python3 university_upc.py
