from .base_task import BaseTask
from utils import get_code
import subprocess
import sys
import os
import shutil
import tempfile


class ExecuteSceneTask(BaseTask):
    def __init__(self, scene_editor):
        super().__init__('Scene Execution')
        self.scene_editor = scene_editor
        self.process = None
        self.temp = tempfile.TemporaryDirectory()
        self.file = self.temp.name + '/runner/main.py'

    def run(self):
        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        self.scene_editor._close()
        code = get_code(self.scene_editor.scene, self.scene_editor.path)
        shutil.copytree(self.scene_editor.path, os.path.dirname(self.file))
        shutil.copytree('fragment', os.path.dirname(self.file) + '/fragment')
        shutil.copy('python_file/main.py', self.file)

        fp = open(self.file, 'w')
        fp.write(code)
        fp.close()

        os.chdir(os.path.dirname(self.file))
        self.process = subprocess.Popen([sys.executable, self.file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while self.process.poll() is None:
            self.new_text_chunk.emit(self.process.stdout.readline())
        if self.process.poll() != 0:
            self.new_error_chunk.emit(self.process.stderr.read())
        self.new_text_chunk.emit('\nExecution ended with exit code ' + str(self.process.poll()))

        os.chdir(os.path.dirname(os.path.dirname(__file__)))
        self.finished.emit()


def execute_scene(editor):
    return ExecuteSceneTask(editor)
