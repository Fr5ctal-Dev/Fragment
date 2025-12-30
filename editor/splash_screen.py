from editor.utils.path import get_resource_path
from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
from pathlib import Path


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.pixmap = QPixmap(str(get_resource_path(Path('fragment') / 'icon' / 'splash_screens' / 'logo.png')))
        self.setStyleSheet('background-color: #121212')

    def resizeEvent(self, event):
        self.update()
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        size = self.size()
        max_width = size.width() // 3
        max_height = size.height() // 3
        scaled_pixmap = self.pixmap.scaled(max_width, max_height, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        x = (size.width() - scaled_pixmap.width()) // 2
        y = (size.height() - scaled_pixmap.height()) // 2
        painter.drawPixmap(x, y, scaled_pixmap)
