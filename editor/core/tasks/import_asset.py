from .base_task import BaseTask
from ..importers import IMPORTERS
from editor.config.filetypes import suffix_to_filetype
from PySide6 import QtCore


def inverse_dictionary(dict):
    inverse_dict = {}
    for name, keys in list(dict.items()):
        for key in keys:
            inverse_dict[key] = name
    return inverse_dict


class ImportAssetWorker(QtCore.QObject):
    finished = QtCore.Signal()
    def __init__(self, path, files):
        super().__init__()
        self.path = path
        self.files = files
        self.is_terminating = False

    def run(self):
        for file in self.files:
            if self.is_terminating:
                break
            importer_type = suffix_to_filetype(file.suffix)
            if importer_type is None:
                importer_type = 'base_importer'
            importer = IMPORTERS[importer_type](self.path)
            importer.import_file(file)
        self.finished.emit()

    def terminate(self):
        self.is_terminating = True


class ImportAssetTask(BaseTask):
    def __init__(self, path, files):
        super().__init__('Import Assets', False)
        self.path = path
        self.files = files

        self.worker = None
        self.worker_thread = None

    def run(self):
        self.worker = ImportAssetWorker(self.path, self.files)
        self.worker_thread = QtCore.QThread()
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_finished)
        self.worker_thread.start()

    def on_finished(self):
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
        self.finished.emit()

    def terminate(self):
        if self.worker:
            self.worker.terminate()
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()


def import_asset(path, files):
    return ImportAssetTask(path, files)
