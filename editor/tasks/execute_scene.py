from .base_task import BaseTask
from editor.utils.python import python_executable
import subprocess
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
        self.scene_editor.save()
        code = f'import fragment.main\nfragment.main.setup("{self.scene_editor.scene}", "{self.scene_editor.path}")'
        shutil.copytree(self.scene_editor.path, os.path.dirname(self.file))

        with open(self.file, 'w') as f:
            f.write(code)

        self.process = subprocess.Popen([python_executable, self.file], cwd=os.path.dirname(self.file), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while self.process.poll() is None:
            pass
        
        if self.process.poll() != 0:
            self.new_error_chunk.emit(self.process.stderr.read())
        self.new_text_chunk.emit('\nExecution ended with exit code ' + str(self.process.poll()))

        self.process.wait()
        self.temp.cleanup()

        self.finished.emit()

    def terminate(self):
        if self.process is not None:
            self.process.terminate()


def execute_scene(editor):
    return ExecuteSceneTask(editor)
