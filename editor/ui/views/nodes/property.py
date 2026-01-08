from ..properties import PropertyView
from PySide6 import QtWidgets
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction


class PropertyNameWidget(QtWidgets.QWidget):
    # A label widget that shows a blue stripe if overridden

    override_changed = Signal(object)

    def __init__(self, properties, text, overridden=False):
        super().__init__()
        self.node_properties = properties
        self.text = text
        self.display_text = text.split('/')[-1]
        self.overridden = overridden
        
        self.main_layout = QtWidgets.QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stripe = QtWidgets.QWidget()
        self.stripe.setFixedWidth(5)
        self.main_layout.addWidget(self.stripe)

        if self.overridden:
            self.override()

        self.label = QtWidgets.QLabel(self.display_text)
        self.main_layout.addWidget(self.label)

        self.override_action = QAction('Enable Override', self)
        self.override_action.triggered.connect(self.override)
        self.override_action.triggered.connect(lambda: self.override_changed.emit(True))
        
        self.unoverride_action = QAction('Disable Override', self)
        self.unoverride_action.triggered.connect(self.unoverride)
        self.unoverride_action.triggered.connect(lambda: self.override_changed.emit(False))

    def override(self):
        self.overridden = True
        self.show_stripe()

    def unoverride(self):
        self.overridden = False
        self.hide_stripe()

    def show_stripe(self):
        self.stripe.setStyleSheet('background-color: #4682b4;')

    def hide_stripe(self):
        self.stripe.setStyleSheet('background-color: none;')

    def contextMenuEvent(self, event):
        context_menu = QtWidgets.QMenu(self)

        if self.overridden:
            self.override_action.setEnabled(False)
            self.unoverride_action.setEnabled(True)
        else:
            self.override_action.setEnabled(True)
            self.unoverride_action.setEnabled(False)
        
        if self.node_properties.target_scene is None:
            self.override_action.setEnabled(False)
            self.unoverride_action.setEnabled(False)

        context_menu.addAction(self.override_action)
        context_menu.addAction(self.unoverride_action)
        context_menu.exec(self.mapToGlobal(event.pos()))


class NodePropertyView(PropertyView):
    def __init__(self, editor):
        super().__init__(editor)

    def display(self):
        super().display()
        assert self.model is not None  # For type checker
        self.title_widget = PropertyNameWidget(self.model.source_model, self.model.name, overridden=self.model.scene_override)
        self.title_widget.override_changed.connect(self.on_override_changed)

    def on_override_changed(self, overridden):
        assert self.model is not None  # For type checker
        if overridden:
            self.model.scene_override = True
        else:
            self.model.scene_override = False
