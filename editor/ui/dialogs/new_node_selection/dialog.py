from ..selection import SelectionDialog
from editor.tools.utils.path import get_resource_path
from ..node_type_selection import NodeTypeSelectionDialog
from PySide6 import QtWidgets, QtGui
from pathlib import Path


class NewNodeSelectionDialog(SelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'New Node')
        self.resize(400, 400)

        self.node_selection_panel = QtWidgets.QHBoxLayout()
        self.central_layout.addLayout(self.node_selection_panel)

        self.node_type_label = QtWidgets.QLabel('Node Type:')
        self.node_selection_panel.addWidget(self.node_type_label)

        self.node_type_button = QtWidgets.QPushButton()
        self.node_type_button.clicked.connect(self.select_node_type)
        self.node_selection_panel.addWidget(self.node_type_button)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText('Name')
        self.central_layout.addWidget(self.name_edit)

        self.info_label = QtWidgets.QLabel()
        self.central_layout.addWidget(self.info_label)

        self.node_type = 'Node'

    def select_node_type(self):
        dialog = NodeTypeSelectionDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            self.node_type = dialog.node_type

    @property
    def node_name(self):
        return self.name_edit.text() if self.name_edit.text() else self.node_type
    
    @property
    def node_type(self):
        return self.current_node_type
    
    @node_type.setter
    def node_type(self, value: str):
        self.current_node_type = value
        self.node_type_button.setText(value)
        self.node_type_button.setIcon(QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'node' / f'{value.lower()}.svg'))))
        self.enable_continue()
