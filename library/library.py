from editor.editor import launch_editor
from editor.utils.path import get_resource_path
from editor.splash_screen import SplashScreen
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QApplication, QWidget, QStackedLayout
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebChannel import QWebChannel
from qdarktheme import setup_theme
from pathlib import Path
import platform
import sys
import json
import shutil
import tempfile


class Backend(QtCore.QObject):
    projectsUpdated = QtCore.Signal('QVariant')

    def __init__(self, parent=None):
        super().__init__(parent)
        self.editor_instances = []
        self.config_path_folder = 'fragment_library_temp'

        _ = self.config_path()

        self.check_projects_timer = QtCore.QTimer(self)
        self.check_projects_timer.timeout.connect(self.check_for_missing_projects)
        self.check_projects_timer.start(1000)

    @QtCore.Slot(result='QVariant')
    def getProjects(self):
        return {'projects': self._string_project_list()}

    @QtCore.Slot()
    def newProject(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(None, 'New Project', '/')
        if not path:
            return
        path = Path(path)
        try:
            path.mkdir()
        except Exception:
            return
        try:
            with open(path / 'main.fragment', 'w') as f:
                f.write('{\'reopen\': {\'tabs\': [], \'last_tab\': None}}')
            shutil.copytree(str(get_resource_path(Path('fragment'))), str(path / 'fragment'))
            (path / 'scenes').mkdir()
            (path / 'scripts').mkdir()
            (path / 'assets').mkdir()
            self._add_to_project_list(path)
            self.openInEditor(path)
        finally:
            self._emit_projects()

    @QtCore.Slot()
    def openProject(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(None, 'Open Project', '/', 'Fragment Projects (*.fragment)')
        if not path:
            return
        path = Path(path)
        project_root = path.parent
        self._add_to_project_list(project_root)
        self.openInEditor(project_root)
        self._emit_projects()

    @QtCore.Slot(str)
    def openInEditor(self, path: str | Path):
        if not path:
            return
        if isinstance(path, str):
            path = Path(path)
        self.editor_instances.append(launch_editor(path))

    def _emit_projects(self):
        self.projectsUpdated.emit({'projects': self._string_project_list()})

    def _projects_list(self):
        projects = self._read_projects()
        items = [{'name': name, 'path': p} for name, p in projects.items() if p.exists()]
        items.sort(key=lambda x: x['name'].lower())
        return items
    
    def _string_project_list(self):
        project_list = self._projects_list()
        return [{'name': item['name'], 'path': item['path'].as_posix()} for item in project_list]

    def _add_to_project_list(self, path):
        projects = self._read_projects()
        projects[path.name] = path
        self._write_projects(projects)

    def check_for_missing_projects(self):
        changed = False
        projects = self._read_projects()
        pruned = {k: v for k, v in projects.items() if v.exists()}
        if len(pruned) != len(projects):
            changed = True
            self._write_projects(pruned)
        if changed:
            self._emit_projects()

    def config_path(self):
        base_temp = Path(tempfile.gettempdir())
        target = base_temp / self.config_path_folder
        if not target.exists():
            self._create_config_folder(target)
        return target

    def _create_config_folder(self, path: Path):
        path.mkdir(parents=True, exist_ok=True)
        cfg = path / 'projects.json'
        if not cfg.exists():
            with open(cfg, 'w') as f:
                f.write('{}')

    def _read_projects(self):
        cfg = self.config_path() / 'projects.json'
        try:
            with open(cfg, 'r') as f:
                json_projects = json.loads(f.read() or '{}')
        except Exception:
            return {}
        
        projects = {}
        for name, path in json_projects.items():
            projects[name] = Path(path)
        return projects

    def _write_projects(self, projects: dict):
        cfg = self.config_path() / 'projects.json'
        json_projects = {}
        for name, path in projects.items():
            json_projects[name] = path.as_posix()

        with open(cfg, 'w') as f:
            f.write(json.dumps(json_projects))

class Library(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.view = QWebEngineView(self)
        self.main_layout.addWidget(self.view)

        self.backend = Backend(self)

        self.channel = QWebChannel(self.view.page())
        self.channel.registerObject('backend', self.backend)
        self.view.page().setWebChannel(self.channel)

        with open(get_resource_path(Path('library') / 'library.html'), 'r') as f:
            html = f.read()

        self.view.setHtml(html, QtCore.QUrl('qrc:///'))
        self.view.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)


def launch_library():
    app = QApplication([])

    setup_theme()

    if platform.system() == 'Windows':
        app.setWindowIcon(QtGui.QIcon(str(get_resource_path(Path('fragment') / 'icon' / 'icon_win.ico'))))
    else:
        app.setWindowIcon(QtGui.QIcon(str(get_resource_path(Path('fragment') / 'icon' / 'icon.png'))))

    window = QWidget()
    window.setWindowTitle('Fragment Library')
    window_layout = QStackedLayout(window)

    library = Library()
    window_layout.addWidget(library)

    splash = SplashScreen()
    window_layout.addWidget(splash)

    window_layout.setCurrentWidget(splash)
    window.resize(1000, 600)
    window.show()

    timer = QtCore.QTimer()
    timer.setSingleShot(True)
    timer.timeout.connect(lambda: window_layout.setCurrentWidget(library))
    timer.start(1000)

    sys.exit(app.exec())
