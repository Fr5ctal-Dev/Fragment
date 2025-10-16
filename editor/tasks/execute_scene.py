from .base_task import BaseTask
from PySide6 import QtCore, QtWidgets, QtGui
from editor.utils.python import python_executable
import os
import shutil
import tempfile


class PythonRunner(QtWidgets.QWidget):
    terminated = QtCore.Signal()
    def __init__(self, script_file):
        super().__init__()
        self.script_file = script_file
        self.init_ui()
        self.init_process()
        
    def init_ui(self):
        self.setWindowTitle(f'Running: {self.script_file}')
        self.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout()

        self.output = QtWidgets.QTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(QtGui.QFont('Consolas', 10))
        layout.addWidget(self.output)
        
        self.setLayout(layout)

        self.normal_format = QtGui.QTextCharFormat()
        self.normal_format.setForeground(QtGui.QColor(255, 255, 255))

        self.error_format = QtGui.QTextCharFormat()
        self.error_format.setForeground(QtGui.QColor(255, 20, 20))

        self.info_format = QtGui.QTextCharFormat()
        self.info_format.setForeground(QtGui.QColor(150, 150, 255))

    def init_process(self):
        self.process = QtCore.QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.process_finished)

        self.append_text(f'Running: {python_executable} {self.script_file}\n', self.info_format)
        self.process.start(python_executable, ['-u', self.script_file])

    def append_text(self, text, text_format):
        cursor = self.output.textCursor()
        cursor.movePosition(QtGui.QTextCursor.MoveOperation.End)
        cursor.insertText(text, text_format)
        self.output.setTextCursor(cursor)
        self.output.ensureCursorVisible()

    @QtCore.Slot()
    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = data.data().decode('utf-8', errors='replace')
        self.append_text(text, self.normal_format)

    @QtCore.Slot()
    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = data.data().decode('utf-8', errors='replace')
        self.append_text(text, self.error_format)

    @QtCore.Slot()
    def process_finished(self, exit_code, exit_status):
        self.append_text(f'\n[Process finished with exit code: {exit_code}]', self.info_format)

    def terminate(self):
        if self.process.state() == QtCore.QProcess.ProcessState.Running:
            self.process.kill()
            self.process.waitForFinished()
        
    def closeEvent(self, event):
        self.terminated.emit()
        return super().closeEvent(event)


class ExecuteSceneTask(BaseTask):
    def __init__(self, scene_editor):
        super().__init__('Scene Execution')
        self.scene_editor = scene_editor
        self.python_runner = None
        self.temp = tempfile.TemporaryDirectory()
        self.file = self.temp.name + '/runner/main.py'

    def run(self):
        self.scene_editor.save()
        code = f'import fragment.main\nfragment.main.setup("{self.scene_editor.scene}", "{self.scene_editor.path}")'
        shutil.copytree(self.scene_editor.path, os.path.dirname(self.file))

        with open(self.file, 'w') as f:
            f.write(code)

        self.python_runner = PythonRunner(self.file)
        self.python_runner.show()
        self.python_runner.terminated.connect(self.terminate)

    def terminate(self):
        if self.python_runner is not None:
            self.python_runner.terminate()
            self.python_runner.close()
        self.temp.cleanup()
        self.finished.emit()


def execute_scene(editor):
    return ExecuteSceneTask(editor)
