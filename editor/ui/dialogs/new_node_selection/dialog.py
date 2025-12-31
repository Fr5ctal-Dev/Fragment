from ..selection import SelectionDialog
from editor.tools.utils.path import get_resource_path
from PySide6 import QtWidgets, QtGui
from pathlib import Path


class NewNodeSelectionDialog(SelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'New Node')
        self.resize(400, 400)

        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.setMinimumWidth(300)
        self.node_tree.setColumnCount(1)
        self.node_tree.setHeaderLabels(['Type'])
        self.node_tree.setIndentation(20)
        self.node_tree.itemClicked.connect(self.enable_continue)
        self.central_layout.addWidget(self.node_tree)

        with open(get_resource_path(Path('editor') / 'assets' / 'config' / 'nodes' / 'tree.vtree')) as f:
            content = f.read()

        indentation = {}

        for line in content.split('\n'):
            widget = QtWidgets.QTreeWidgetItem([line.strip()])
            widget.setIcon(0, QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'node' / f'{line.strip()}.png'))))
            indent = len(line.split(' ')) - 1
            indentation[indent] = widget
            if indent == 0:
                self.node_tree.addTopLevelItem(widget)

            else:
                indentation[indent - 1].addChild(widget)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText('Name')
        self.central_layout.addWidget(self.name_edit)

        self.info_label = QtWidgets.QLabel()
        self.central_layout.addWidget(self.info_label)

    @property
    def node_name(self):
        return self.name_edit.text() if self.name_edit.text() else self.node_type
    
    @property
    def node_type(self):
        return self.node_tree.currentItem().text(0)
