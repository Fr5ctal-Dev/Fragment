from PySide6.QtWidgets import QLabel
from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QCursor


class Tooltip(QLabel):
    def __init__(self, text='', parent=None):
        super().__init__(text, parent)
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.adjustSize()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_position)
        self.offset = QPoint(10, -30)

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start(0)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

    def update_position(self):
        pos = QCursor.pos()
        self.move(pos + self.offset)
