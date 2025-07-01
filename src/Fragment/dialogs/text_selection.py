from .selection import SelectionDialog
from PySide6 import QtWidgets


class TextSelectionDialog(SelectionDialog):
    def __init__(self, parent, title, placeholder_text=''):
        super().__init__(parent, title)
        self.resize(400, 100)
        self.line_edit = QtWidgets.QLineEdit()
        self.line_edit.setPlaceholderText(placeholder_text)
        self.line_edit.textEdited.connect(self.validate_input)
        self.central_layout.addWidget(self.line_edit)

    def validate_input(self, text):
        if text.strip():
            self.enable_continue()
        else:
            self.disable_continue()
