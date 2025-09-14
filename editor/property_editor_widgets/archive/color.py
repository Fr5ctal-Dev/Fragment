from .editor_widget import EditorWidget
from PySide6.QtWidgets import QPushButton, QColorDialog


class Color(EditorWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.color_button = QPushButton()
        self.main_layout.addWidget(self.color_button)
        self.update_editor()
        self.color_button.clicked.connect(self.ask_for_color)

    def ask_for_color(self):
        color = QColorDialog.getColor()
        if not color.isValid():
            return
        hex = color.name()
        rgb = color.red() / 255, color.green() / 255, color.blue() / 255
        self.set_color(hex, rgb)
        self.change_property()

    def set_color(self, hex, rgb):
        self.setStyleSheet(f'background-color: {hex};')
        self.value = rgb

    def update_editor(self):
        self.set_color('#%02x%02x%02x' % (int(self.value[0] * 255), int(self.value[1] * 255), int(self.value[2] * 255)), self.value)
