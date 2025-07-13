import subprocess
import sys


def run(path):
    process = subprocess.Popen([sys.executable, path + '/main.py'], stdout=subprocess.PIPE, text=True)
    return process
