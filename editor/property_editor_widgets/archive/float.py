from .editor_widget import EditorWidget
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt


class DraggableSpinBox(QtWidgets.QDoubleSpinBox):
    def __init__(self):
        super().__init__()
        self.setStyleSheet('QAbstractSpinBox::up-button, QAbstractSpinBox::down-button { width: 30px; height: 10px; border: none; background: none; background-color: #3C3C3C}')
        self.setSingleStep(0)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self.rect().contains(event.position().toPoint()):
            delta = event.position().toPoint().x() - self.previous_mouse_position.x()
            current_value = self.value()
            self.setValue(current_value + delta * 0.1)
            QtGui.QCursor.setPos(self.mapToGlobal(self.previous_mouse_position))
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.previous_mouse_position = event.position().toPoint()
            self.setCursor(Qt.CursorShape.BlankCursor)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)


class Float(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.spin_box = DraggableSpinBox()
        self.main_layout.addWidget(self.spin_box)
        self.spin_box.setRange(-99999.9, 99999.9)
        self.spin_box.setDecimals(2)

        self.update_editor()
        self.spin_box.valueChanged.connect(self.change_property)

    def update_data(self):
        self.value = self.spin_box.value()

    def update_editor(self):
        self.spin_box.setValue(self.value)
