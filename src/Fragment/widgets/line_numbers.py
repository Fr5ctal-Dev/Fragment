from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt


class LineNumberWidget(QtWidgets.QWidget):
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.editor.textChanged.connect(self.update_width)
        self.editor.verticalScrollBar().valueChanged.connect(self.update_on_scroll)
        self.update_width()

    def update_width(self):
        self.setFixedWidth(self.line_number_area_width())
        self.update()

    def line_number_area_width(self):
        space = 3 + self.fontMetrics().horizontalAdvance('99999')
        return space

    def calculate_line_count(self):
        return self.editor.document().blockCount()

    def update_on_scroll(self):
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.fillRect(event.rect(), QtGui.QColor(50, 50, 50))

        block = self.editor.document().firstBlock()
        block_number = block.blockNumber()

        scroll_offset = self.editor.verticalScrollBar().value()

        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.setFont(QtGui.QFont('Consolas', 12))

        while block.isValid():
            block_top = self.editor.document().documentLayout().blockBoundingRect(block).translated(0, -scroll_offset).top()

            if block.isVisible() and block_top >= event.rect().top() and block_top <= event.rect().bottom():
                number = ' ' + str(block_number + 1)
                painter.drawText(0, int(block_top), self.width(), self.fontMetrics().height(), Qt.AlignmentFlag.AlignLeft, number)

            block = block.next()
            block_number += 1
