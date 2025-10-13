from editor.property_editor_widgets import EDITOR_WIDGETS
from PySide6.QtCore import Signal, QObject


class Property(QObject):
    value_changed = Signal()

    def __init__(self, name, type, value, node_type, scene_override=False):
        super().__init__()
        self.name = name
        self.type = type
        self._value = value
        self.node_type = node_type
        self.scene_override = scene_override
        self.editor_widget = None

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        changed = new_value != self._value
        self._value = new_value
        self.update_editor_value()

        if changed:
            self.value_changed.emit()

    def setup_property_editor(self, scene_editor):
        self.editor_widget = EDITOR_WIDGETS[self.type](scene_editor, self.node_type, self.value, self.type, self.name)
        self.editor_widget.value_changed.connect(self.on_editor_value_changed)

    def on_editor_value_changed(self, new_value):
        self.value = new_value

    def update_editor_value(self):
        if self.editor_widget is not None:
            self.editor_widget.value = self.value
            self.editor_widget.update_editor()

    def to_data(self):
        return {
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'scene_override': self.scene_override
        }
