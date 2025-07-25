from PySide6.QtWidgets import QApplication, QPlainTextEdit, QWidget, QMainWindow
from PySide6.QtGui import QPainter, QColor, QFont
from PySide6.QtCore import Qt

class LineNumberWidget(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        self.editor.blockCountChanged.connect(self.update_width)
        self.editor.updateRequest.connect(self.update_on_request)
        self.update_width()

    def update_width(self):
        self.setFixedWidth(3 + self.fontMetrics().horizontalAdvance('99999'))
        self.update()

    def update_on_request(self, rect, dy):
        if dy:
            self.scroll(0, dy)
        else:
            self.update(0, rect.y(), self.width(), rect.height())
        if rect.contains(self.editor.viewport().rect()):
            self.update_width()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(event.rect(), QColor(50, 50, 50))
        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        line_height = int(self.editor.blockBoundingRect(block).height())
        offset = self.editor.contentOffset().y()
        top = int(self.editor.blockBoundingGeometry(block).translated(offset, 0).top())
        bottom = top + line_height
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont('Consolas', 12))
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.drawText(0, top, self.width(), self.fontMetrics().height(), Qt.AlignLeft, str(block_number + 1))
            block = block.next()
            block_number += 1
            top = bottom
            bottom = top + line_height

class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberWidget(self)
        self.setViewportMargins(self.lineNumberArea.width(), 0, 0, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(cr.x(), cr.y(), self.lineNumberArea.width(), cr.height())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.editor = CodeEditor()
        self.setCentralWidget(self.editor)
        self.editor.setPlainText("")

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
