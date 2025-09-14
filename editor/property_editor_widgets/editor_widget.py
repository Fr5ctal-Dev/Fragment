from PySide6.QtWidgets import QWidget, QHBoxLayout
from PySide6.QtCore import Signal


class EditorWidget(QWidget):
    value_changed = Signal(object)
    def __init__(self, scene_editor, node_type, value, type, name):
        super().__init__()
        self.scene_editor = scene_editor
        self.node_type = node_type
        self.path = self.scene_editor.path

        self.type = type
        self.value = value
        self.name = name

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def update_data(self):
        """Updates self.value accordingly."""
        pass

    def change_property(self):
        """Should be called when value is changed."""
        self.update_data()
        self.value_changed.emit(self.value)

    def update_editor(self):
        """Call when self.value is changed without the editor knowing, to update editor."""
        pass

    def get(self):
        """Calls self.update_data and returns the updated value."""
        self.update_data()
        return self.value
