# PeekDock 中文说明

*查看 [English](README.md) 版*

PeekDock 是一个使用 Python 与 Qt 编写的小工具，提供一个半透明的停靠窗口。将其他窗口拖入其中即可创建实时缩略图，原窗口会自动最小化并保留在任务栏中。

## 功能
- 可调大小的半透明主窗口
- 自动列出当前系统可见窗口
- 将列表中的窗口条目拖入中央区域即可创建预览
- 预览窗口会持续更新，并按缩放比例显示
- 拖入后原窗口会被最小化，但缩略图仍会实时刷新

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
