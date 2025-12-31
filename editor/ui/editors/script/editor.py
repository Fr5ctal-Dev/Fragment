from editor.ui.widgets.script_editor import ScriptEditor as ScriptEditor_
from ..editor import Editor
from PySide6 import QtWidgets


class ScriptEditor(Editor):
    def __init__(self, path, editor, script):
        super().__init__(path, editor, script)
        self.script = script

        self.central_widget = QtWidgets.QWidget()
        self.central_widget_layout = QtWidgets.QStackedLayout(self.central_widget)
        self.central_widget_layout.setSpacing(0)
        self.central_widget_layout.setContentsMargins(0, 0, 0, 0)

        self.script_editor = ScriptEditor_(script, path)

        self.loading_screen = QtWidgets.QWidget()
        self.loading_screen_layout = QtWidgets.QHBoxLayout(self.loading_screen)
        self.loading_progress = QtWidgets.QProgressBar()
        self.loading_progress.setRange(0, 100)
        self.loading_progress.setTextVisible(False)

        spacer1 = QtWidgets.QWidget()
        spacer2 = QtWidgets.QWidget()

        self.loading_screen_layout.addWidget(spacer1, stretch=1)
        self.loading_screen_layout.addWidget(self.loading_progress, stretch=1)
        self.loading_screen_layout.addWidget(spacer2, stretch=1)

        self.central_widget_layout.addWidget(self.loading_screen)
        self.central_widget_layout.addWidget(self.script_editor)
        self.central_widget_layout.setCurrentWidget(self.loading_screen)

        self.script_editor.loadProgress.connect(lambda progress: self.loading_progress.setValue(progress))
        self.script_editor.loadFinished.connect(lambda: self.central_widget_layout.setCurrentWidget(self.script_editor))
        
        self.setCentralWidget(self.central_widget)

    def save(self):
        super().save()
        self.script_editor.save()
