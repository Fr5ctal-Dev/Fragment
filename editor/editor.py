from .editors.scene import SceneEditor
from .editors.script import ScriptEditor

from editor.widgets.filesystem import FileSystem
from editor.widgets.task_manager import TaskManager
from editor.widgets.notifications import Notifications

from editor.utils.path import get_resource_path

from PySide6 import QtWidgets, QtGui, QtCore, QtWebEngineWidgets
from PySide6.QtCore import Qt

from pathlib import Path
import json

with open(get_resource_path(Path('editor') / 'filetypes' / 'filetypes.json')) as f:
    FILETYPES = json.loads(f.read())

with open(get_resource_path(Path('editor') / 'filetypes' / 'uncreatable.json')) as f:
    FILETYPES = {**FILETYPES, **json.loads(f.read())}

for name, ext in FILETYPES.items():
    FILETYPES[name] = Path(ext)

def get_filetype(path: Path):
    for name, ext in FILETYPES.items():
        if path.suffix == ext.suffix:
            return name


def launch_editor(path: Path):
    window = EditorWindow()
    window_layout = QtWidgets.QStackedLayout(window)

    editor = Editor(path)
    window_layout.addWidget(editor)
    dummy_widget = QtWebEngineWidgets.QWebEngineView()
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

        self.tab_view = QtWidgets.QTabWidget()
        self.setCentralWidget(self.tab_view)
        self.tab_view.setMovable(True)
        self.tab_view.setTabsClosable(True)
        self.tab_view.setUsesScrollButtons(True)
        self.tab_view.setDocumentMode(True)
        self.tab_view.tabCloseRequested.connect(self.delete_tab)
        self.tab_view.currentChanged.connect(self.save_tabs)

        self.file_system_dock = QtWidgets.QDockWidget()
        self.file_system_dock.setWindowTitle('Files')
        self.file_system_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.file_system = FileSystem(self, self.path)
        self.file_system.doubleClicked.connect(lambda index: self.open(Path(self.file_system.directory_model.filePath(index)).relative_to(self.path)))
        self.file_system_dock.setWidget(self.file_system)
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

        self.reopen_last()

    def save_settings(self):
        with open(self.path / 'main.fragment') as f:
            content = eval(f.read())

        content['reopen']['tabs'] = list([self.tab_view.widget(e).file.as_posix() for e in range(self.tab_view.count())])
        content['reopen']['last_tab'] = self.tab_view.currentIndex()

        with open(self.path / 'main.fragment', 'w') as f:
            f.write(str(content))

    def reopen_last(self):
        with open(self.path / 'main.fragment') as f:
            content = eval(f.read())

        tabs = content['reopen']['tabs']
        last_tab = content['reopen']['last_tab']

        for tab in tabs:
            self.open(Path(tab))
        if last_tab is not None:
            self.tab_view.setCurrentIndex(last_tab)

    def save_tabs(self):
        for i in range(self.tab_view.count()):
            self.tab_view.widget(i).save()

    def new_tab(self, editor, name):
        self.tab_view.setCurrentIndex(self.tab_view.addTab(editor(self.path), QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'file_icons' / f'{get_filetype(Path(name)).lower()}.png'))), name))

    def delete_tab(self, index):
        self.tab_view.widget(index).cleanup()
        self.tab_view.removeTab(index)

    def open(self, path):
        if not (self.path / path).exists():
            return

        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == path.name:
                self.tab_view.setCurrentIndex(i)
                return

        filetype = get_filetype(path)
        if filetype is None: # Unsupported file format
            return
        filetype = filetype.lower()
        if filetype == 'scene':
            self.new_tab(lambda _path: SceneEditor(_path, self, path), path.name)

        if filetype == 'script':
            self.new_tab(lambda _path: ScriptEditor(_path, self, path), path.name)

    def cleanup(self):
        self.save_tabs()
        self.save_settings()
        for i in range(self.tab_view.count()):
            self.delete_tab(0)
        self.task_manager.cleanup()
