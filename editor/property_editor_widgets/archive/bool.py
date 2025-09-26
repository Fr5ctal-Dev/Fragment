from .editor_widget import EditorWidget
from PySide6.QtWidgets import QCheckBox


class Bool(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.check_box = QCheckBox()
        self.main_layout.addWidget(self.check_box)
        self.update_editor()
        self.check_box.checkStateChanged.connect(self.change_property)

    def update_data(self):
        self.value = self.check_box.isChecked()

    def update_editor(self):
        self.check_box.setChecked(self.value)
