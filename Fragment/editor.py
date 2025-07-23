import sys

from editors.scene import SceneEditor
from editors.script import ScriptEditor

from widgets.filesystem import FileSystem
from widgets.task_manager import TaskManager
from widgets.notifications import Notifications

from splash_screen import SplashScreen

from qdarktheme import setup_theme

from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt

import os
import json
import platform

fp = open('filetypes/filetypes.json')
FILETYPES = json.loads(fp.read())
fp.close()

fp = open('filetypes/uncreatable.json')
FILETYPES = {**FILETYPES, **json.loads(fp.read())}
fp.close()

def get_filetype(path):
    for name, ext in FILETYPES.items():
        if path.endswith(ext.split('.')[-1]):
            return name


def launch_editor():
    app = QtWidgets.QApplication([])
    setup_theme()
    if platform.system() == 'Windows':
        app.setWindowIcon(QtGui.QIcon('fragment/icon/icon_win.ico'))
    else:
        app.setWindowIcon(QtGui.QIcon('fragment/icon/icon.png'))

    window = EditorWindow()
    window_layout = QtWidgets.QStackedLayout(window)

    splash = SplashScreen()
    window_layout.addWidget(splash)

    window_layout.setCurrentWidget(splash)
    window.showMaximized()

    editor = Editor(sys.argv[1])
    window_layout.addWidget(editor)
    window_layout.setCurrentWidget(editor)

    window.closed.connect(editor.save_settings)

    sys.exit(app.exec())


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
        self.tab_view.currentChanged.connect(lambda index: (self.save_tabs(), self.reload_tab(index)))

        self.file_system_dock = QtWidgets.QDockWidget()
        self.file_system_dock.setWindowTitle('Files')
        self.file_system_dock.setAllowedAreas(Qt.DockWidgetArea.AllDockWidgetAreas)
        self.file_system = FileSystem(self, self.path)
        self.file_system.doubleClicked.connect(lambda index: self.open(self.file_system.directory_model.filePath(index)))
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
        fp = open(self.path + '/main.fragment')
        content = eval(fp.read())
        fp.close()

        content['reopen']['tabs'] = list([self.tab_view.widget(e).file for e in range(self.tab_view.count())])
        content['reopen']['last_tab'] = self.tab_view.currentIndex()

        fp = open(self.path + '/main.fragment', 'w')
        fp.write(str(content))
        fp.close()

        for i in range(self.tab_view.count()):
            self.delete_tab(0)

    def reopen_last(self):
        fp = open(self.path + '/main.fragment')
        content = eval(fp.read())
        fp.close()

        tabs = content['reopen']['tabs']
        last_tab = content['reopen']['last_tab']

        for tab in tabs:
            self.open(tab)
        if last_tab is not None:
            self.tab_view.setCurrentIndex(last_tab)

    def save_tabs(self):
        for i in range(self.tab_view.count()):
            self.tab_view.widget(i)._close()

    def reload_tab(self, index):
        if self.tab_view.widget(index) is not None:
            self.tab_view.widget(index)._reload()

    def new_tab(self, editor, name):
        self.tab_view.setCurrentIndex(self.tab_view.addTab(editor(self.path), QtGui.QIcon(f'assets/file_icons/{get_filetype(name).lower()}.png'), name))

    def delete_tab(self, index):
        self.tab_view.widget(index)._close()
        self.tab_view.widget(index)._destroy()
        self.tab_view.removeTab(index)

    def open(self, path):
        if not os.path.exists(path):
            return

        for i in range(self.tab_view.count()):
            if self.tab_view.tabText(i) == os.path.basename(path):
                self.tab_view.setCurrentIndex(i)
                return

        filetype = get_filetype(path).lower()
        if filetype == 'scene':
            for i in range(self.tab_view.count()):
                if isinstance(self.tab_view.widget(i), SceneEditor):
                    self.delete_tab(i)
                    break
            self.new_tab(lambda _path: SceneEditor(_path, self, path), os.path.basename(path))

        if filetype == 'script':
            self.new_tab(lambda _path: ScriptEditor(_path, self, path), os.path.basename(path))


launch_editor()
