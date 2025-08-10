from editor import launch_editor
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout
from PySide6 import QtGui
from splash_screen import SplashScreen
from qdarktheme import setup_theme
import platform
import sys
import os
import json
import shutil


class Library(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.editor_instances = []

        self.check_projects_timer = QtCore.QTimer()
        self.check_projects_timer.timeout.connect(self.check_for_missing_projects)
        self.check_projects_timer.start(1000)

        self.main_layout = QtWidgets.QHBoxLayout(self)

        self.tab_list = QtWidgets.QFrame()
        self.tab_list_frame = QtWidgets.QVBoxLayout(self.tab_list)
        self.project_tab_button = QtWidgets.QPushButton()
        self.project_tab_button.setText('Projects')
        self.project_tab_button.setFixedSize(QtCore.QSize(200, 50))
        self.project_tab_button.clicked.connect(lambda: self.main_stacked_layout.setCurrentWidget(self.project_frame))
        self.tab_list_frame.addWidget(self.project_tab_button)
        self.main_layout.addWidget(self.tab_list)

        self.main_stacked_layout = QtWidgets.QStackedLayout()
        self.main_layout.addLayout(self.main_stacked_layout)

        self.project_frame = QtWidgets.QFrame()
        self.project_layout = QtWidgets.QGridLayout(self.project_frame)
        self.project_list_frame = QtWidgets.QFrame()
        self.project_list_layout = QtWidgets.QGridLayout(self.project_list_frame)
        self.project_list = QtWidgets.QTreeWidget()
        self.project_list.itemDoubleClicked.connect(lambda item, column: self.open_in_editor(item.text(1)))
        self.project_list.setColumnCount(2)
        self.project_list.setHeaderLabels(['Name', 'Path'])
        self.project_list_layout.addWidget(self.project_list, 0, 0)
        self.load_project_list()
        self.project_layout.addWidget(self.project_list_frame, 0, 0)
        self.button_frame = QtWidgets.QFrame()
        self.button_frame.setFixedSize(QtCore.QSize(200, 100))
        self.button_layout = QtWidgets.QVBoxLayout(self.button_frame)
        self.new_project_button = QtWidgets.QPushButton()
        self.new_project_button.setText('New')
        self.new_project_button.clicked.connect(self.new_project)
        self.open_project_button = QtWidgets.QPushButton()
        self.open_project_button.setText('Open')
        self.open_project_button.clicked.connect(self.open_project)
        self.button_layout.addWidget(self.new_project_button)
        self.button_layout.addWidget(self.open_project_button)
        self.project_layout.addWidget(self.button_frame, 0, 1)
        self.main_stacked_layout.addWidget(self.project_frame)

    def open_in_editor(self, path):
        self.editor_instances.append(launch_editor(path))

    def add_to_project_list(self, path):
        with open('library_config/projects.json') as f:
            projects = json.loads(f.read())
        projects[os.path.basename(path)] = path
        with open('library_config/projects.json', 'w') as f:
            f.write(json.dumps(projects))
        self.load_project_list()

    def new_project(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'New Project', '/')[0]
        if not path:
            return

        try:
            os.mkdir(path)
        except:
            return

        with open(path + '/main.fragment', 'w') as f:
            f.write("{'reopen': {'tabs': [], 'last_tab': None}}")

        shutil.copytree('fragment', path + '/fragment')

        os.mkdir(path + '/scenes')
        os.mkdir(path + '/scripts')
        os.mkdir(path + '/assets')

        self.add_to_project_list(path)
        self.open_in_editor(path)

    def open_project(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Project', '/', 'Fragment Projects (*.fragment)')[0]
        if not path:
            return
        path = os.path.dirname(path)

        self.add_to_project_list(path)
        self.open_in_editor(path)

    def load_project_list(self):
        self.project_list.clear()
        with open('library_config/projects.json') as f:
            projects = json.loads(f.read())
        delete = []
        for project in projects.keys():
            if not os.path.exists(projects[project]):
                delete.append(project)
                continue
            item = QtWidgets.QTreeWidgetItem([project, projects[project]])
            item.setSizeHint(0, QtCore.QSize(1, 40))
            self.project_list.addTopLevelItem(item)

        for key in delete:
            projects.pop(key)

        with open('library_config/projects.json', 'w') as f:
            f.write(json.dumps(projects))

    def check_for_missing_projects(self):
        with open('library_config/projects.json') as f:
            projects = json.loads(f.read())

        for project in projects.values():
            if not os.path.exists(project):
                self.load_project_list()
                return



def launch_library():
    app = QApplication([])
    setup_theme()
    if platform.system() == 'Windows':
        app.setWindowIcon(QtGui.QIcon('fragment/icon/icon_win.ico'))
    else:
        app.setWindowIcon(QtGui.QIcon('fragment/icon/icon.png'))

    window = QWidget()
    window.setWindowTitle('Fragment Library')
    window_layout = QStackedLayout(window)

    library = Library()
    window_layout.addWidget(library)

    splash = SplashScreen()
    window_layout.addWidget(splash)

    window_layout.setCurrentWidget(splash)
    window.showMaximized()

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: window_layout.setCurrentWidget(library))
    timer.start(1000)

    sys.exit(app.exec())
