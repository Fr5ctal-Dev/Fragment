from editor.ui.widgets.editor_view import EditorView
from editor.ui.widgets.task_manager import TaskManager
from editor.ui.widgets.notifications import Notifications
from editor.ui.views.inspector import InspectorView
from editor.ui.views.filesystem import FileSystemView
from editor.core.models.filesystem import FileSystemModel

from PySide6 import QtWidgets, QtCore, QtQuickWidgets
from PySide6.QtCore import Qt

from pathlib import Path


def launch_editor(path: Path):
    window = EditorWindow()
    window_layout = QtWidgets.QStackedLayout(window)

    editor = Editor(path)
    window_layout.addWidget(editor)
    dummy_widget = QtQuickWidgets.QQuickWidget()
    window_layout.addWidget(dummy_widget)

    window_layout.setCurrentWidget(dummy_widget)
    QtCore.QTimer.singleShot(10, lambda: window_layout.setCurrentWidget(editor))

    window.closed.connect(editor.cleanup)
    window.showMaximized()
    return window


class EditorWindow(QtWidgets.QWidget):
    closed = QtCore.Signal()
    def __init__(self):
        super().__init__()
        self.resize(2200, 1300)
        self.setGeometry(0, 0, 2200, 1300)
        self.setWindowTitle('Fragment Editor')

    def closeEvent(self, event):
        self.closed.emit()
        super().closeEvent(event)


class Editor(QtWidgets.QMainWindow):
    def __init__(self, path):
        super().__init__()
        self.path = path

        self.editor_view = EditorView(self)
        self.setCentralWidget(self.editor_view)

        self.file_system_dock = QtWidgets.QDockWidget()
        self.file_system_dock.setWindowTitle('Files')
        self.file_system_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.file_system_model = FileSystemModel(self, self.path)
        self.file_system_view = FileSystemView(self)
        self.file_system_view.set_model(self.file_system_model)
        assert self.file_system_view.filesystem_tree is not None # For type checker
        self.file_system_dock.setWidget(self.file_system_view.filesystem_tree)
        self.file_system_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.file_system_dock)

        self.bottom_dock = QtWidgets.QDockWidget()
        self.bottom_dock.setWindowTitle('Consoles')
        self.bottom_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.docked_tabview = QtWidgets.QTabWidget()
        self.docked_tabview.setMovable(True)
        self.docked_tabview.setDocumentMode(True)
        self.console = QtWidgets.QTextEdit()
        self.console.setReadOnly(True)
        self.docked_tabview.addTab(self.console, 'Console')
        self.task_manager = TaskManager(self)
        self.docked_tabview.addTab(self.task_manager, 'Task Manager')
        self.notifications = Notifications(self)
        self.docked_tabview.addTab(self.notifications, 'Notifications')
        self.bottom_dock.setWidget(self.docked_tabview)
        self.bottom_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.bottom_dock)

        self.inspector_dock = QtWidgets.QDockWidget()
        self.inspector_dock.setWindowTitle('Inspector')
        self.inspector_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.inspector_dock.setFeatures(QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetMovable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetFloatable | QtWidgets.QDockWidget.DockWidgetFeature.DockWidgetClosable)
        self.inspector = InspectorView(self)
        self.inspector.set_model(None)
        self.inspector_dock.setWidget(self.inspector.main_widget)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspector_dock)

    def open(self, path: Path):
        self.editor_view.select_new_file(path)

    def set_inspector_model(self, property_model):
        self.inspector.set_model(property_model)

    def cleanup(self):
        self.editor_view.cleanup()
        self.task_manager.cleanup()
        self.file_system_model.cleanup()
        self.file_system_view.cleanup()
