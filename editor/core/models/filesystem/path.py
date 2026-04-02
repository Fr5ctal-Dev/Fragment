from ..properties import PropertiesModel, Property
from PySide6.QtCore import Signal


class PathModel(PropertiesModel):
    named_changed = Signal()
    def __init__(self, editor, name: str):
        super().__init__()
        self.editor = editor
        self.name = name
        self.set_property('Name', self.name)
        self.properties['Name'].value_changed.connect(self.named_changed.emit)

    @property
    def default_properties(self):
        properties = {
            'Name': Property(self, 'Name', 'string', ''),
        }
        return {**properties, **super().default_properties}
