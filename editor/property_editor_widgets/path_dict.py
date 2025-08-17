from .list_editor_base import BaseListEditor
from .path import Path
from PySide6.QtWidgets import QLineEdit


class PathDict(BaseListEditor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.add_button.clicked.connect(lambda: self.add_item('', ''))
        self.update_editor()

    def add_item(self, key, value):
        line_edit = QLineEdit()
        line_edit.setText(key)
        line_edit.textChanged.connect(self.change_property)
        item = self.new_item()
        path_edit = Path([value, 'path'], *self.args[1:], **self.kwargs)
        path_edit.value_changed.connect(lambda *args: self.change_property())
        self.tree_widget.setItemWidget(item, 0, line_edit)
        self.tree_widget.setItemWidget(item, 1, path_edit)

    def update_editor(self):
        for item in self.value.keys():
            self.add_item(item, self.value[item])

    def update_data(self):
        data = {}
        for item in self.items:
            data[self.tree_widget.itemWidget(item, 0).text()] = self.tree_widget.itemWidget(item, 1).get()
        self.value = data
