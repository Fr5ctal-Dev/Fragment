from ..base_view import BaseView
from editor.ui.widgets.editor_widgets import EDITOR_WIDGETS
from PySide6 import QtWidgets


class PropertyView(BaseView):
    def __init__(self, editor):
        super().__init__(editor)
        self.title_widget = None
        self.editor_widget = None

    def cleanup(self):
        super().cleanup()
        if self.model is not None:
            self.model.value_changed.disconnect(self.on_model_value_changed)
        if self.title_widget:
            self.title_widget.deleteLater()
        if self.editor_widget:
            self.editor_widget.deleteLater()
        self.title_widget = None
        self.editor_widget = None

    def display(self):
        assert self.model is not None  # For type checker
        self.title_widget = QtWidgets.QLabel(self.model.name.rsplit('/')[-1])
        self.editor_widget = EDITOR_WIDGETS[self.model.type](self.editor, self.model.source_model, self.model.value, self.model.type, self.model.name)
        self.editor_widget.value_changed.connect(self.on_editor_value_changed)
        self.model.value_changed.connect(self.on_model_value_changed)

    def on_editor_value_changed(self):
        assert self.model is not None  # For type checker
        if self.editor_widget:
            self.model.value = self.editor_widget.get()

    def on_model_value_changed(self):
        assert self.model is not None  # For type checker
        if self.editor_widget:
            self.editor_widget.value = self.model.value
            self.editor_widget.update_editor()
