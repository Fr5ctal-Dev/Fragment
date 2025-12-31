from PySide6 import QtWidgets
from PySide6.QtCore import Qt


class Inspector(QtWidgets.QWidget):
    def __init__(self, scene_editor):
        super().__init__()
        self.scene_editor = scene_editor
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.inspector_view = QtWidgets.QStackedWidget()
        self.main_layout.addWidget(self.inspector_view)

        self.current_inspector = QtWidgets.QWidget()
        current_inspector_layout = QtWidgets.QVBoxLayout(self.current_inspector)
        current_inspector_label = QtWidgets.QLabel('Nothing selected', alignment=Qt.AlignmentFlag.AlignCenter)
        current_inspector_layout.addWidget(current_inspector_label)
        self.inspector_view.addWidget(self.current_inspector)

    def set_inspector(self, widget):
        if self.current_inspector:
            self.inspector_view.removeWidget(self.current_inspector)
        self.current_inspector = widget
        self.inspector_view.addWidget(self.current_inspector)
        self.inspector_view.setCurrentWidget(self.current_inspector)
