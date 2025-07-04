# PeekDock 中文说明

*查看 [English](README.md) 版*

PeekDock 是一个使用 Python 与 Qt 编写的小工具，提供一个半透明的停靠窗口，可以把其他窗口以缩略图形式放在其中，既不会完全缩到任务栏，也不会占满桌面。

## 功能
- 可调大小的半透明主窗口
- 自动列出当前系统可见窗口
- 将列表中的窗口条目拖入中央区域即可收纳
- 收纳后的窗口依旧保持实时显示

### 运行要求
- Windows 10/11
- Python 3.9 及以上
- 依赖库：`PyQt5`、`pywin32`

### 源码运行
```bash
pip install PyQt5 pywin32
python main.py
```

### 打包为单一 exe
安装 PyInstaller 后执行：
```bash
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```
在 `dist/main.exe` 即可得到独立的可执行文件。
