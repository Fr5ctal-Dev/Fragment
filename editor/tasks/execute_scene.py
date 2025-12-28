from .base_task import BaseTask
from PySide6 import QtCore
from editor.utils.python import python_executable
from editor.utils.path import get_resource_path
from pathlib import Path
import shutil
import tempfile


class GameView(QtCore.QObject):
    window_closed = QtCore.Signal()
    def __init__(self, port):
        super().__init__()
        self.port = port
        self.terminated = False
        self.process = QtCore.QProcess()
        self.process.finished.connect(self.on_process_finished)
        self.process.start(python_executable, [str(get_resource_path(Path('editor') / 'http_server' / 'view.py')), str(self.port)])

    def on_process_finished(self):
        self.process.waitForFinished()
        self.terminated = True
        self.window_closed.emit()

    def terminate(self):
        if self.process is not None:
            self.process.kill()
            self.process.waitForFinished()
        self.terminated = True


class HTTPServer(QtCore.QObject):
    server_started = QtCore.Signal()
    def __init__(self, script_file, project_path):
        super().__init__()
        self.script_file = script_file
        self.project_path = project_path

        self.process = QtCore.QProcess()
        self.process.readyReadStandardError.connect(self.check_port)
        self.process.start(python_executable, ['-u', str(get_resource_path(Path('editor') / 'http_server' / 'main.py')), str(self.project_path)])
        self.port = None

    def check_port(self):
        if self.process is None:
            return
        
        if self.port is not None:
            return

        port_text = self.process.readAllStandardError().data().decode('utf-8')
        if port_text:
            try:
                self.port = int(port_text.strip())
                self.server_started.emit()
            except ValueError:
                pass

    def terminate(self):
        if self.process is not None:
            self.process.kill()
            self.process.waitForFinished()
            self.process = None


class ExecuteSceneTask(BaseTask):
    def __init__(self, scene_editor):
        super().__init__('Scene Execution')
        self.scene_editor = scene_editor
        self.python_runner = None
        self.temp = tempfile.TemporaryDirectory()
        self.file = Path(self.temp.name) / 'runner' / 'index.html'
        self.http_server = None
        self.game_view = None

    def run(self):
        self.scene_editor.save()
        code = '''
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Fragment Engine</title>
  <style>
    body {
      margin: 0;
    }
  </style>
</head>
<body>
  <script type="importmap">
    {
      "imports": {
        "pixi.js": "https://cdn.jsdelivr.net/npm/pixi.js@latest/dist/pixi.min.mjs"
      }
    }
  </script>

  <script type="module">
    import { setup } from '/fragment/main.js';

    setup('${}', '');
  </script>
</body>
</html>

        '''.replace('${}', str(self.scene_editor.scene.as_posix())).strip()
        shutil.copytree(self.scene_editor.path, self.file.parent)

        with open(self.file, 'w') as f:
            f.write(code)

        self.http_server = HTTPServer(self.file, self.file.parent)
        self.http_server.server_started.connect(self.create_game_view)

    def create_game_view(self):
        if self.http_server is not None and self.http_server.port is not None:
            self.game_view = GameView(self.http_server.port)
            self.game_view.window_closed.connect(self.terminate)

    def terminate(self):
        if self.game_view is not None and not self.game_view.terminated:
            self.game_view.terminate()
        if self.http_server is not None:
            self.http_server.terminate()
        self.temp.cleanup()
        self.finished.emit()


def execute_scene(editor):
    return ExecuteSceneTask(editor)
