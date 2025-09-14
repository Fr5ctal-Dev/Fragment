from .editor_widget import EditorWidget
from ..widgets.draggable_spinbox import DraggableSpinBox
from PySide6.QtWidgets import QVBoxLayout, QSpacerItem


class Vector2(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.vector2_layout = QVBoxLayout()
        self.vector2_layout.setContentsMargins(0, 0, 0, 0)
        self.vector2_layout.setSpacing(1)
        self.main_layout.addLayout(self.vector2_layout)

        self.vector2_layout.addItem(QSpacerItem(3, 6))

        self.x_spin_box = DraggableSpinBox()
        self.y_spin_box = DraggableSpinBox()
        self.vector2_layout.addWidget(self.x_spin_box)
        self.vector2_layout.addWidget(self.y_spin_box)
        self.x_spin_box.setRange(-99999.9, 99999.9)
        self.y_spin_box.setRange(-99999.9, 99999.9)
        self.x_spin_box.setDecimals(2)
        self.y_spin_box.setDecimals(2)

        self.vector2_layout.addItem(QSpacerItem(3, 6))

        self.update_editor()
        self.x_spin_box.valueChanged.connect(self.change_property)
        self.y_spin_box.valueChanged.connect(self.change_property)

    def update_data(self):
        self.value = (self.x_spin_box.value(), self.y_spin_box.value())

    def update_editor(self):
        self.x_spin_box.setValue(self.value[0])
        self.y_spin_box.setValue(self.value[1])
