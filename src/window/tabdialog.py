from PyQt6.QtWidgets import QDialog, QGridLayout, QWidget
from PyQt6 import uic
from PyQt6.QtGui import QIcon, QKeyEvent
from PyQt6.QtCore import Qt

from gm_resources import resourcePath


class TabDialog(QDialog):
    def __init__(self, tab, callBack, parent=None):
        super().__init__(parent)
        try:
            uic.loadUi(resourcePath("src/window/ui/tabdialog.ui"), self)
        except Exception as e:
            print(f"Failed to load UI: {e}")
        self.layout().addWidget(tab)
        self._tab = tab
        self.setWindowIcon(QIcon(resourcePath("src/resources/icon.ico")))
        self.setWindowFlag(Qt.WindowType.FramelessWindowHint, True)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)
        self._callBack = callBack
        self._drag_pos = None
        self._resize_pos = None
        self._resize_margin = 10
        self.setMouseTracking(True)
        layout = self.layout()
        if isinstance(layout, QGridLayout):
            layout.setContentsMargins(0, 0, 0, 0)

    def getTab(self):
        return self._tab

    def closeEvent(self, event):
        self._callBack(self)
        event.accept()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            if self._is_resize_zone(event.pos()):
                self._resize_pos = event.globalPosition().toPoint()
                event.accept()
            else:
                self._drag_pos = event.globalPosition().toPoint()
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                event.accept()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._resize_pos:
            delta = event.globalPosition().toPoint() - self._resize_pos
            new_width = self.width() + delta.x()
            new_height = self.height() + delta.y()
            self.resize(new_width, new_height)
            self._resize_pos = event.globalPosition().toPoint()
            event.accept()
        elif self._drag_pos and event.buttons() == Qt.MouseButton.LeftButton and event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
        else:
            if self._is_resize_zone(event.pos()):
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        self._resize_pos = None
        self.setCursor(Qt.CursorShape.ArrowCursor)
        event.accept()

    def _is_resize_zone(self, pos):
        rect = self.rect()
        return (pos.x() >= rect.right() - self._resize_margin and
                pos.y() >= rect.bottom() - self._resize_margin)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Shift:
            self._set_widgets_mouse_events(False)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Shift:
            self._set_widgets_mouse_events(True)
        super().keyReleaseEvent(event)

    def _set_widgets_mouse_events(self, enable: bool):
        for widget in self.findChildren(QWidget):
            widget.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, not enable)
