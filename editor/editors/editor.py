from PySide6 import QtWidgets


class Editor(QtWidgets.QMainWindow):
    def __init__(self, path, editor, file):
        super().__init__()
        self.path = path
        self.editor = editor
        self.file = file

    def save(self):
        pass

    def delete(self):
        self.save()
