import sys

# Only run on Windows
if sys.platform != 'win32':
    raise SystemExit('PeekDock currently supports Windows only.')

from PyQt5 import QtWidgets, QtGui, QtCore
import win32gui
import win32ui
import win32con


def capture_window(hwnd):
    """Return QPixmap of a window using PrintWindow, even if minimized."""
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    width, height = right - left, bottom - top

    hwnd_dc = win32gui.GetWindowDC(hwnd)
    mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
    save_dc = mfc_dc.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfc_dc, width, height)
    save_dc.SelectObject(bitmap)

    result = win32gui.PrintWindow(hwnd, save_dc.GetSafeHdc(), 2)

    bmpinfo = bitmap.GetInfo()
    bmpstr = bitmap.GetBitmapBits(True)

    win32gui.DeleteObject(bitmap.GetHandle())
    save_dc.DeleteDC()
    mfc_dc.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwnd_dc)

    if result != 1:
        return None

    image = QtGui.QImage(bmpstr, bmpinfo['bmWidth'], bmpinfo['bmHeight'],
                         bmpinfo['bmWidthBytes'], QtGui.QImage.Format_RGB32)
    return QtGui.QPixmap.fromImage(image.rgbSwapped())



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


class ThumbnailWidget(QtWidgets.QLabel):
    """Widget displaying a periodically updated screenshot of a window."""

    def __init__(self, hwnd, parent=None):
        super().__init__(parent)
        self.hwnd = hwnd
        self.setScaledContents(True)
        self.setFixedSize(200, 150)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_thumbnail)
        self.timer.start(500)
        self.update_thumbnail()

    def update_thumbnail(self):
        pix = capture_window(self.hwnd)
        if pix:
            pix = pix.scaled(self.size(), QtCore.Qt.KeepAspectRatio,
                             QtCore.Qt.SmoothTransformation)
            self.setPixmap(pix)



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
        thumb = ThumbnailWidget(hwnd)
        sub = self.addSubWindow(thumb)
        sub.setWindowTitle(title)
        sub.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        sub.resize(200, 150)
        sub.show()
        self.docked[hwnd] = sub
        sub.destroyed.connect(lambda: self.docked.pop(hwnd, None))
        # Minimize original window to free desktop space
        win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)



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
