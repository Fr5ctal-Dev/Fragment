from .selection import SelectionDialog
from PySide6 import QtWidgets, QtGui


class NewNodeSelectionDialog(SelectionDialog):
    def __init__(self, parent, ignore_parent=False):
        super().__init__(parent, 'New Node')
        self.resize(400, 400)
        if ignore_parent:
            self.title_label.setText('Set Root Node')

        self.node_tree = QtWidgets.QTreeWidget()
        self.node_tree.setMinimumWidth(300)
        self.node_tree.setColumnCount(1)
        self.node_tree.setHeaderLabels(['Type'])
        self.node_tree.setIndentation(20)
        self.node_tree.itemClicked.connect(self.enable_continue)
        self.central_layout.addWidget(self.node_tree)

        fp = open('node_properties/tree.vtree')
        content = fp.read()
        fp.close()
        indentation = {}

        for line in content.split('\n'):
            widget = QtWidgets.QTreeWidgetItem([line.strip()])
            widget.setIcon(0, QtGui.QIcon(f'assets/node_icons/{line.strip()}.png'))
            indent = len(line.split(' ')) - 1
            indentation[indent] = widget
            if indent == 0:
                self.node_tree.addTopLevelItem(widget)

            else:
                indentation[indent - 1].addChild(widget)

        if not ignore_parent:
            self.name_edit = QtWidgets.QLineEdit()
            self.name_edit.setPlaceholderText('Name')
            self.central_layout.addWidget(self.name_edit)

        if not ignore_parent:
            self.info_label = QtWidgets.QLabel()
            self.central_layout.addWidget(self.info_label)
