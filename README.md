# PeekDock

*Read this in [中文](README_CN.md).* 

PeekDock is a small Python/Qt application that provides a translucent dock window. You can drag entries representing other windows into this dock so they remain visible as small thumbnails instead of being fully minimized.

## Features
- Semi-transparent, resizable main window
- List of all visible windows on the system
- Drag an entry from the list into the dock area to embed the window
- Each docked window stays live in a smaller form

### Requirements
- Windows 10/11
- Python 3.9 or newer
- Packages: `PyQt5`, `pywin32`

### Run from source
```bash
pip install PyQt5 pywin32
python main.py
```

### Create a single executable
Install PyInstaller and build:
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```
The generated `dist/main.exe` can run without Python installed.
