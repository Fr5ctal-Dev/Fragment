from .editor_widget import EditorWidget
from ..widgets.draggable_spinbox import DraggableSpinBox


class Float(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.spin_box = DraggableSpinBox()
        self.main_layout.addWidget(self.spin_box)
        self.spin_box.setRange(-99999.9, 99999.9)
        self.spin_box.setDecimals(2)
        
        self.update_editor()
        self.spin_box.valueChanged.connect(self.change_property)

    def update_data(self):
        self.value = self.spin_box.value()

    def update_editor(self):
        self.spin_box.setValue(self.value)
