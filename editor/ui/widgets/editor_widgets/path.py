from .editor_widget import EditorWidget
from editor.tools.utils.path import extract_extensions_from_filter, get_resource_path
from editor.ui.widgets.filesystem import FileIconProvider
from editor.ui.dialogs.file_selection import get_open_relative_file_name
from PySide6.QtWidgets import QPushButton, QLineEdit, QLabel, QSpacerItem
from PySide6.QtGui import QIcon
from PySide6.QtCore import QFileInfo
from pathlib import Path as PathLib
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
        self.path_selection_button.setIcon(QIcon(str(get_resource_path(PathLib('editor') / 'assets' / 'icons' / 'file' / 'folder.png'))))
        self.path_selection_button.clicked.connect(lambda: self.select_path()) # Do not remove 'lambda'
        self.open_path_button = QPushButton()
        self.main_layout.addWidget(self.open_path_button)
        self.open_path_button.setIcon(QIcon(str(get_resource_path(PathLib('editor') / 'assets' / 'icons' / 'ui' / 'open.png'))))
        self.open_path_button.clicked.connect(self.open_path)

        self.update_file_icon()
        self.update_editor()

    def select_path(self, filter=FILE_FILTER):
        path = get_open_relative_file_name(self, self.path, 'Select Path', filter)
        if not path:
            return
        self.value = path.as_posix()

        self.update_editor()
        self.change_property()

    def open_path(self):
        if not self.value:
            return
        self.scene_editor.editor.open(PathLib(self.value))

    def update_file_icon(self):
        if not self.FILE_FILTER:
            return
        self.path_icon_display.setPixmap(self.file_icon_provider.icon(QFileInfo('file' + extract_extensions_from_filter(self.FILE_FILTER)[0])).pixmap(15, 15))

    def update_editor(self):
        self.path_display.setReadOnly(False)
        self.path_display.setText(os.path.basename(self.value))
        self.path_display.setReadOnly(True)
        self.update_file_icon()
        