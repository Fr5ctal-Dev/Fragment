from .path_script import PathScript
from editor.tools.utils.path import get_resource_path
from editor.ui.dialogs.file_selection import get_save_relative_file_name
from PySide6.QtWidgets import QPushButton
from PySide6.QtGui import QIcon
from pathlib import Path


class PathNodeScript(PathScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.node_type = self.source_model.type
        self.create_script_button = QPushButton()
        self.main_layout.addWidget(self.create_script_button)
        self.create_script_button.setIcon(QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'ui' / 'plus.svg'))))
        self.create_script_button.clicked.connect(self.create_node_script)

    def create_node_script(self):
        code = '''// Node Script
import { ''' + self.node_type + ''' as ParentNodeType } from '/fragment/nodes/''' + self.node_type.lower() + '''.js';

export class Node extends ParentNodeType { }'''
        path = get_save_relative_file_name(self, self.path, 'New Script')
        if not path:
            return

        path = path.with_suffix('.js').as_posix()
        with open(self.path / path, 'w') as f:
            f.write(code)

        self.value = path
        self.update_editor()
        self.change_property()

        self.open_path()
