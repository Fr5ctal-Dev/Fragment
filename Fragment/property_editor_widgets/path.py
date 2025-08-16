from .editor_widget import EditorWidget
from utils.path import extract_extensions_from_filter, get_resource_path
from widgets.filesystem import FileIconProvider
from PySide6.QtWidgets import QPushButton, QLineEdit, QFileDialog, QLabel, QSpacerItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFileInfo
import os


class Path(EditorWidget):
    FILE_FILTER = 'All Files (*.*)'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.file_icon_provider = FileIconProvider()
        self.path_icon_display = QLabel()
        self.main_layout.addWidget(self.path_icon_display)
        self.main_layout.addSpacerItem(QSpacerItem(5, 5))
        self.path_display = QLineEdit()
        self.main_layout.addWidget(self.path_display)
        self.path_display.setText(self.value)
        self.path_display.setReadOnly(True)
        self.path_selection_button = QPushButton()
        self.main_layout.addWidget(self.path_selection_button)
        self.path_selection_button.setIcon(QIcon(get_resource_path('assets/file_icons/folder.png')))
        self.path_selection_button.clicked.connect(lambda: self.select_path()) # Do not remove 'lambda'
        self.open_path_button = QPushButton()
        self.main_layout.addWidget(self.open_path_button)
        self.open_path_button.setIcon(QIcon(get_resource_path('assets/ui_icons/open.png')))
        self.open_path_button.clicked.connect(self.open_path)

        self.update_file_icon()
        self.update_editor()

    def select_path(self, filter=FILE_FILTER):
        path = QFileDialog.getOpenFileName(self, 'Select Path', self.path, filter)[0]
        if not path:
            return
        self.value = path

        self.update_editor()
        self.change_property()

    def open_path(self):
        if not self.value:
            return
        self.scene_editor.editor.open(self.value)

    def update_file_icon(self):
        if not self.FILE_FILTER:
            return
        self.path_icon_display.setPixmap(self.file_icon_provider.icon(QFileInfo('file' + extract_extensions_from_filter(self.FILE_FILTER)[0])).pixmap(15, 15))

    def update_editor(self):
        self.path_display.setReadOnly(False)
        self.path_display.setText(os.path.basename(self.value))
        self.path_display.setReadOnly(True)
