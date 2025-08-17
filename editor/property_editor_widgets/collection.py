from .editor_widget import EditorWidget
from PySide6.QtWidgets import QVBoxLayout


class Collection(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs

        self.collection_layout = QVBoxLayout()
        self.collection_layout.setContentsMargins(0, 0, 0, 0)
        self.collection_layout.setSpacing(1)

        self.main_layout.addLayout(self.collection_layout)
        self.editors = []

    def add_editor(self, editor_class, data):
        editor = editor_class(data, *self.args[1:], **self.kwargs)
        self.collection_layout.addWidget(editor)

        editor.value_changed.connect(self.change_property)

        self.editors.append(editor)

    def update_data(self):
        data = []
        for editor in self.editors:
            data.append(editor.get())
        self.value = data
