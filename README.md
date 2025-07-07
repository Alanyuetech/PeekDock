# PeekDock

*Read this in [中文](README_CN.md).* 

PeekDock is a small Python/Qt application that provides a translucent dock window. Drag entries representing other windows into this dock to keep live thumbnails on screen without affecting the original windows or their taskbar icons.


## Features
- Semi-transparent, resizable main window
- List of all visible windows on the system
- Drag an entry from the list into the dock area to create a preview
- Each docked window shows a continuously updated, scaled screenshot


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
