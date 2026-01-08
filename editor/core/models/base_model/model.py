from PySide6 import QtCore


class BaseModel(QtCore.QObject):
    deleted = QtCore.Signal()
    
    def cleanup(self):
        self.deleted.emit()
        self.deleteLater()
