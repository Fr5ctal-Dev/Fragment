from .editor_widget import EditorWidget
from PySide6.QtWidgets import QLabel


class Hidden(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = QLabel('None')
        self.main_layout.addWidget(self.label)
