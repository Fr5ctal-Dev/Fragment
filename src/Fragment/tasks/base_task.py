from PySide6.QtCore import QObject, Signal


class BaseTask(QObject):
    finished = Signal()
    new_text_chunk = Signal(str)
    new_error_chunk = Signal(str)

    def __init__(self, name, determinate=False):
        super().__init__()
        self.name = name
        self.determinate = determinate

    def run(self):
        pass
