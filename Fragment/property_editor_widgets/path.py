from .editor_widget import EditorWidget
from PySide6.QtWidgets import QPushButton, QLineEdit, QFileDialog
from PySide6.QtGui import QIcon


class Path(EditorWidget):
    FILE_FILTER = '*.*'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.path_display = QLineEdit()
        self.main_layout.addWidget(self.path_display)
        self.path_display.setText(self.value)
        self.path_display.setReadOnly(True)
        self.path_selection_button = QPushButton()
        self.main_layout.addWidget(self.path_selection_button)
        self.path_selection_button.setIcon(QIcon('assets/file_icons/folder.png'))
        self.path_selection_button.clicked.connect(lambda: self.select_path()) # Do not remove 'lambda'

        self.update_editor()

    def select_path(self, filter=FILE_FILTER):
        path = QFileDialog.getOpenFileName(self, 'Select Path', self.path, filter)[0]
        if not path:
            return
        self.value = path

        self.update_editor()
        self.change_property()

    def update_editor(self):
        self.path_display.setReadOnly(False)
        self.path_display.setText(self.value)
        self.path_display.setReadOnly(True)
