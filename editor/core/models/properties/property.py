from editor.core.models.base_model import BaseModel
from PySide6.QtCore import Signal


class Property(BaseModel):
    value_changed = Signal()

    def __init__(self, source_model, name, type, value):
        super().__init__()
        self.source_model = source_model # Source property model
        self.name = name
        self.type = type
        self._value = value

    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        changed = new_value != self._value
        self._value = new_value

        if changed:
            self.value_changed.emit()
