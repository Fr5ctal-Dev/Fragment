from editor.utils.python import python_executable
import subprocess


def run(path):
    process = subprocess.Popen([python_executable, path + '/main.py'], stdout=subprocess.PIPE, text=True)
    return process
