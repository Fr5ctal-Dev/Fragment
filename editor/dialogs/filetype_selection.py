from .selection import SelectionDialog
from editor.utils.path import get_resource_path
from PySide6 import QtWidgets, QtGui
import json

with open(get_resource_path('editor/filetypes/filetypes.json'), 'r') as f:
    filetypes = json.loads(f.read())


class FiletypeSelectionDialog(SelectionDialog):
    def __init__(self, parent):
        super().__init__(parent, 'New File')
        self.resize(400, 400)
        self.filelist = QtWidgets.QListWidget()
        self.filelist.itemClicked.connect(lambda item: self.enable_continue())
        self.central_layout.addWidget(self.filelist)

        for file in filetypes.keys():
            list_item = QtWidgets.QListWidgetItem(QtGui.QIcon(get_resource_path(f'editor/assets/file_icons/{file}.png')), file)
            self.filelist.addItem(list_item)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText('Name')
        self.name_edit.textChanged.connect(self.enable_continue)
        self.central_layout.addWidget(self.name_edit)
