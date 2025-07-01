from PySide6 import QtWidgets, QtCore
import sys
import subprocess
import shutil
import os
import json


class Library(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.processes = []

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
        self.project_list.itemDoubleClicked.connect(lambda item, column: self.processes.append(subprocess.Popen([sys.executable, 'editor.py', item.text(1)])))
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

    def new_project(self):
        path = QtWidgets.QFileDialog.getSaveFileName(self, 'New Project', '/')[0]
        if not path:
            return
        shutil.copytree('save', path)
        fp = open('library_config/projects.json')
        projects = json.loads(fp.read())
        fp.close()
        projects[os.path.basename(path)] = path
        fp = open('library_config/projects.json', 'w')
        fp.write(json.dumps(projects))
        fp.close()
        self.load_project_list()
        self.processes.append(subprocess.Popen([sys.executable, 'editor.py', path]))

    def open_project(self):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Project', '/', 'Fragment Projects (*.fragment)')[0]
        if not path:
            return
        path = os.path.dirname(path)
        fp = open('library_config/projects.json')
        projects = json.loads(fp.read())
        fp.close()
        projects[os.path.basename(path)] = path
        fp = open('library_config/projects.json', 'w')
        fp.write(json.dumps(projects))
        fp.close()
        self.load_project_list()
        self.processes.append(subprocess.Popen([sys.executable, 'editor.py', path]))

    def closeEvent(self, event):
        for p in self.processes:
            p.terminate()
        return super().closeEvent(event)

    def load_project_list(self):
        self.project_list.clear()
        fp = open('library_config/projects.json')
        projects = json.loads(fp.read())
        fp.close()
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

        fp = open('library_config/projects.json', 'w')
        fp.write(json.dumps(projects))
        fp.close()

    def check_for_missing_projects(self):
        fp = open('library_config/projects.json')
        projects = json.loads(fp.read())
        fp.close()

        for project in projects.values():
            if not os.path.exists(project):
                self.load_project_list()
                return
