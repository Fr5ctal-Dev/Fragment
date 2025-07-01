from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal


class EditorWidget(QWidget):
    value_changed = Signal(QWidget)
    def __init__(self, data, path):
        super().__init__()
        self.type = data[1]
        self.value = data[0]
        self.path = path

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def update_data(self):
        pass

    def change_property(self):
        self.update_data()
        self.value_changed.emit(self)

    def update_editor(self):
        pass

    def get(self):
        self.update_data()
        return self.value
