from widgets.script_editor import ScriptEditor as ScriptEditor_
from widgets.line_numbers import LineNumberWidget
from .editor import Editor
from PySide6 import QtWidgets


class ScriptEditor(Editor):
    def __init__(self, path, editor, script):
        super().__init__(path, editor, script)
        self.script = script

        self.central_widget = QtWidgets.QWidget()
        self.central_widget_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.script_editor = ScriptEditor_(script, path)

        self.line_numbers = LineNumberWidget(self.script_editor)
        self.script_editor.lint_timer.timeout.connect(self.line_numbers.repaint)

        self.central_widget_layout.addWidget(self.line_numbers)
        self.central_widget_layout.addWidget(self.script_editor)
        self.setCentralWidget(self.central_widget)

    def save(self):
        self.script_editor.save()

    def _close(self):
        self.save()

    def _destroy(self):
        self.script_editor.lint_timer.stop()
        self.script_editor.update_timer.stop()
