from .list_editor_base import BaseListEditor
from .string import String


class StringList(BaseListEditor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs
        self.tree_widget.setColumnCount(1)
        self.add_button.clicked.connect(lambda: self.add_item(''))
        self.update_editor()

    def add_item(self, value):
        item = self.new_item()
        string_edit = String([value, 'string'], *self.args[1:], **self.kwargs)
        string_edit.value_changed.connect(lambda *args: self.change_property())
        self.tree_widget.setItemWidget(item, 0, string_edit)
        print(item)

    def update_editor(self):
        for item in self.value:
            self.add_item(item)

    def update_data(self):
        data = []

        for item in self.items:
            data.append(self.tree_widget.itemWidget(item, 0).get())
        self.value = data
