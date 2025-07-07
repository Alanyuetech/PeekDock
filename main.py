import sys

# Only run on Windows
if sys.platform != 'win32':
    raise SystemExit('PeekDock currently supports Windows only.')

from PyQt5 import QtWidgets, QtGui, QtCore
import win32gui
import win32con
import ctypes
from ctypes import wintypes

# DWM API constants and setup
DWM_TNP_RECTDESTINATION = 0x00000001
DWM_TNP_VISIBLE = 0x00000008
DWM_TNP_OPACITY = 0x00000004
DWM_TNP_SOURCECLIENTAREAONLY = 0x00000010

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class DWM_THUMBNAIL_PROPERTIES(ctypes.Structure):
    _fields_ = [
        ("dwFlags", wintypes.DWORD),
        ("rcDestination", RECT),
        ("rcSource", RECT),
        ("opacity", wintypes.BYTE),
        ("fVisible", wintypes.BOOL),
        ("fSourceClientAreaOnly", wintypes.BOOL),
    ]

dwmapi = ctypes.windll.dwmapi
DwmRegisterThumbnail = dwmapi.DwmRegisterThumbnail
DwmRegisterThumbnail.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.POINTER(wintypes.HANDLE)]
DwmRegisterThumbnail.restype = wintypes.HRESULT
DwmUnregisterThumbnail = dwmapi.DwmUnregisterThumbnail
DwmUnregisterThumbnail.argtypes = [wintypes.HANDLE]
DwmUnregisterThumbnail.restype = wintypes.HRESULT
DwmUpdateThumbnailProperties = dwmapi.DwmUpdateThumbnailProperties
DwmUpdateThumbnailProperties.argtypes = [wintypes.HANDLE, ctypes.POINTER(DWM_THUMBNAIL_PROPERTIES)]
DwmUpdateThumbnailProperties.restype = wintypes.HRESULT
DwmQueryThumbnailSourceSize = dwmapi.DwmQueryThumbnailSourceSize
DwmQueryThumbnailSourceSize.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.SIZE)]
DwmQueryThumbnailSourceSize.restype = wintypes.HRESULT

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def refresh(self):
        self.clear()
        for title, hwnd in enum_windows():
            item = QtWidgets.QListWidgetItem(title)
            item.setData(QtCore.Qt.UserRole, hwnd)
            self.addItem(item)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        hwnd = item.data(QtCore.Qt.UserRole)
        mime = QtCore.QMimeData()
        mime.setData('application/x-peekdock-hwnd', str(hwnd).encode())
        drag = QtGui.QDrag(self)
        drag.setMimeData(mime)
        drag.exec_(QtCore.Qt.CopyAction)


class ThumbnailWidget(QtWidgets.QWidget):
    """Widget that shows a live DWM thumbnail of a window."""

    def __init__(self, hwnd, parent=None):
        super().__init__(parent)
        self.hwnd = hwnd
        self.thumbnail = wintypes.HANDLE()
        self.setFixedSize(200, 150)
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        res = DwmRegisterThumbnail(int(self.winId()), hwnd, ctypes.byref(self.thumbnail))
        if res != 0:
            print('Failed to register thumbnail', res)
        self.update_properties()

    def update_properties(self):
        if not self.thumbnail:
            return
        dest = RECT(0, 0, self.width(), self.height())
        source_size = wintypes.SIZE()
        if DwmQueryThumbnailSourceSize(self.thumbnail, ctypes.byref(source_size)) == 0:
            src = RECT(0, 0, source_size.cx, source_size.cy)
        else:
            src = RECT()
        props = DWM_THUMBNAIL_PROPERTIES()
        props.dwFlags = DWM_TNP_RECTDESTINATION | DWM_TNP_VISIBLE
        props.rcDestination = dest
        props.rcSource = src
        props.opacity = 255
        props.fVisible = True
        props.fSourceClientAreaOnly = False
        DwmUpdateThumbnailProperties(self.thumbnail, ctypes.byref(props))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_properties()

    def closeEvent(self, event):
        if self.thumbnail:
            DwmUnregisterThumbnail(self.thumbnail)
            self.thumbnail = wintypes.HANDLE()
        super().closeEvent(event)


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


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
