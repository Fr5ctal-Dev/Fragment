from .editor_widget import EditorWidget
from PySide6.QtWidgets import QLineEdit


class String(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_edit = QLineEdit()
        self.main_layout.addWidget(self.line_edit)
        self.update_editor()
        self.line_edit.textChanged.connect(self.change_property)

    def update_data(self):
        try:
            self.value = eval(self.line_edit.text())

        except:
            self.value = self.line_edit.text()

    def update_editor(self):
        self.line_edit.setText(str(self.value))
