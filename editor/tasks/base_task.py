from PySide6.QtCore import QObject, Signal


class BaseTask(QObject):
    finished = Signal()

    def __init__(self, name, determinate=False):
        super().__init__()
        self.name = name
        self.determinate = determinate

    def run(self):
        pass

    def terminate(self):
        pass
