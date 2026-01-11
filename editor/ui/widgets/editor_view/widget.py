from PySide6 import QtWidgets, QtCore, QtGui
from editor.ui.editors import EDITORS
from editor.ui.editors.editor import Editor
from editor.tools.utils.path import get_resource_path
from pathlib import Path
import json

with open(get_resource_path(Path('editor') / 'config' / 'filetypes' / 'filetypes.json')) as f:
    FILETYPES = json.loads(f.read())

with open(get_resource_path(Path('editor') / 'config' / 'filetypes' / 'uncreatable.json')) as f:
    FILETYPES = {**FILETYPES, **json.loads(f.read())}

for name, ext in FILETYPES.items():
    FILETYPES[name] = Path(ext)

def get_filetype(path: Path):
    for name, ext in FILETYPES.items():
        if path.suffix == ext.suffix:
            return name


class EditorView(QtWidgets.QWidget): # TODO: Implement recent files feature
    def __init__(self, editor):
        super().__init__()
        self.editor = editor
        self.path = editor.path
        self.current_editor: Editor | None = None
        self.back_history: list[Path] = []
        self.forward_history: list[Path] = []

        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.navigation_bar_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.navigation_bar_layout)

        self.button_layout = QtWidgets.QHBoxLayout()
        self.navigation_bar_layout.addLayout(self.button_layout)
        self.back_button = QtWidgets.QPushButton()
        self.forward_button = QtWidgets.QPushButton()
        self.back_button.setIcon(QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'ui' / 'chevron-left.svg'))))
        self.forward_button.setIcon(QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'ui' / 'chevron-right.svg'))))
        self.back_button.setEnabled(False)
        self.forward_button.setEnabled(False)
        self.back_button.clicked.connect(self.select_previous_file)
        self.forward_button.clicked.connect(self.select_next_file)
        self.button_layout.addWidget(self.back_button)
        self.button_layout.addWidget(self.forward_button)

        self.address_bar = QtWidgets.QLineEdit()
        self.address_bar.setReadOnly(True)
        self.navigation_bar_layout.addWidget(self.address_bar)

        self.update_navigation_bar()

        self.editor_layout = QtWidgets.QStackedLayout()
        self.main_layout.addLayout(self.editor_layout)

        self.empty_view = QtWidgets.QLabel('No file opened')
        self.empty_view.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.editor_layout.addWidget(self.empty_view)
        
        self.nonexistent_file_view = QtWidgets.QLabel('File does not exist')
        self.nonexistent_file_view.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.editor_layout.addWidget(self.nonexistent_file_view)
        
        self.editor_layout.setCurrentWidget(self.empty_view)

    def set_current_editor(self, editor: Editor):
        if self.current_editor is not None:
            self.current_editor.cleanup()
            self.editor_layout.removeWidget(self.current_editor)
            self.current_editor.deleteLater()

        self.current_editor = editor
        self.editor_layout.addWidget(editor)
        self.editor_layout.setCurrentWidget(editor)

    def open_file(self, path: Path, filetype):
        if not (self.path / path).exists():
            self.editor_layout.setCurrentWidget(self.nonexistent_file_view)
            self.current_editor = None
            return
        filetype = filetype.lower()
        self.set_current_editor(EDITORS[filetype](self.path, self.editor, path))

    def update_navigation_bar(self, path: Path | None = None):
        self.back_button.setEnabled(len(self.back_history) > 0)
        self.forward_button.setEnabled(len(self.forward_history) > 0)
        if path is not None:
            self.address_bar.setText(str(path))
        else:
            self.address_bar.setText('')

    def select_new_file(self, path: Path):
        if self.current_editor is not None:
            if self.current_editor.file == path:
                return
        
        filetype = get_filetype(path)
        if filetype is None: # Unsupported file format
            return
        if self.current_editor is not None:
            self.back_history.append(self.current_editor.file)
        self.forward_history.clear()
        self.open_file(path, filetype)
        self.update_navigation_bar(path)

    def select_previous_file(self):
        if len(self.back_history) == 0:
            return
        previous_file = self.back_history.pop()
        if self.current_editor is not None:
            self.forward_history.append(self.current_editor.file)
        filetype = get_filetype(previous_file)
        self.open_file(previous_file, filetype)
        self.update_navigation_bar(previous_file)

    def select_next_file(self):
        if len(self.forward_history) == 0:
            return
        next_file = self.forward_history.pop()
        if self.current_editor is not None:
            self.back_history.append(self.current_editor.file)
        filetype = get_filetype(next_file)
        self.open_file(next_file, filetype)
        self.update_navigation_bar(next_file)

    def cleanup(self):
        if self.current_editor is not None:
            self.current_editor.cleanup()
