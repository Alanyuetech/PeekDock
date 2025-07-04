import sys

# Only run on Windows
if sys.platform != 'win32':
    raise SystemExit('PeekDock currently supports Windows only.')

from PyQt5 import QtWidgets, QtGui, QtCore
import win32gui
import win32con


def enum_windows():
    """Return list of (title, handle) tuples for visible windows."""
    results = []

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                results.append((title, hwnd))
        return True

    win32gui.EnumWindows(callback, None)
    return results


class WindowListWidget(QtWidgets.QListWidget):
    """List widget showing open windows."""

    def refresh(self):
        self.clear()
        for title, hwnd in enum_windows():
            item = QtWidgets.QListWidgetItem(title)
            item.setData(QtCore.Qt.UserRole, hwnd)
            self.addItem(item)


class DockArea(QtWidgets.QMdiArea):
    """Area that accepts window handles to dock."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.docked = {}

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-peekdock-hwnd'):
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        data = event.mimeData().data('application/x-peekdock-hwnd')
        hwnd = int(data.data().decode())
        self.dock_window(hwnd)
        event.acceptProposedAction()

    def dock_window(self, hwnd):
        if hwnd in self.docked:
            return
        title = win32gui.GetWindowText(hwnd)
        window = QtGui.QWindow.fromWinId(hwnd)
        container = QtWidgets.QWidget.createWindowContainer(window)
        sub = self.addSubWindow(container)
        sub.setWindowTitle(title)
        sub.resize(200, 150)
        sub.show()
        self.docked[hwnd] = (window, container, sub)
        # set parent at OS level
        win32gui.SetParent(hwnd, int(container.winId()))
        style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
        style = style & ~win32con.WS_POPUP | win32con.WS_CHILD
        win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('PeekDock')
        self.setWindowOpacity(0.8)
        self.resize(800, 600)

        self.list_widget = WindowListWidget()
        self.list_widget.refresh()

        dock_widget = QtWidgets.QDockWidget('Windows', self)
        dock_widget.setWidget(self.list_widget)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, dock_widget)

        self.dock_area = DockArea()
        self.setCentralWidget(self.dock_area)

        self.list_widget.itemPressed.connect(self.start_drag)

    def start_drag(self, item):
        hwnd = item.data(QtCore.Qt.UserRole)
        mime = QtCore.QMimeData()
        mime.setData('application/x-peekdock-hwnd', str(hwnd).encode())
        drag = QtGui.QDrag(self.list_widget)
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.MoveAction)


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
