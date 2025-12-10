from .path_script import PathScript
from editor.utils.path import get_resource_path
from PySide6.QtWidgets import QPushButton, QFileDialog
from PySide6.QtGui import QIcon
from pathlib import Path


class PathNodeScript(PathScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_script_button = QPushButton()
        self.main_layout.addWidget(self.create_script_button)
        self.create_script_button.setIcon(QIcon(str(get_resource_path(Path('editor') / 'assets' / 'ui_icons' / 'add.png'))))
        self.create_script_button.clicked.connect(self.create_node_script)

    def create_node_script(self):
        code = f'# Node Script\nimport fragment.nodes.{self.node_type.lower()}\n\n\nclass Node(fragment.nodes.{self.node_type.lower()}.{self.node_type}):\n    pass\n'
        path = QFileDialog.getSaveFileName(self, 'New Script', str(self.path))[0]
        if not path:
            return

        path += '.py'
        with open(path, 'w') as f:
            f.write(code)

        self.value = path
        self.update_editor()
        self.change_property()

        self.open_path()
