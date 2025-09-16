from editor.property_editor_widgets import EDITOR_WIDGETS


class Property:
    def __init__(self, name, type, value):
        self.name = name
        self.type = type
        self.value = value
        self.editor_widget = None

    def setup_property_editor(self, scene_editor, node_type):
        self.editor_widget = EDITOR_WIDGETS[self.type](scene_editor, node_type, self.value, self.type, self.name)
        self.editor_widget.value_changed.connect(self.on_editor_value_changed)

    def on_editor_value_changed(self, new_value):
        self.value = new_value

    def update_value(self, new_value):
        self.value = new_value
        self.update_editor_value()

    def update_editor_value(self):
        if self.editor_widget is not None:
            self.editor_widget.value = self.value
            self.editor_widget.update_editor()

    def to_data(self):
        return [self.name, self.type, self.value]
