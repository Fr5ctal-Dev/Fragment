from editor.dialogs.filetype_selection import FiletypeSelectionDialog
from editor.dialogs.text_selection import TextSelectionDialog

from editor.utils.path import get_resource_path

from PySide6 import QtWidgets, QtCore, QtGui

from pathlib import Path

import json
import shutil


with open(get_resource_path(Path('editor') / 'filetypes' / 'filetypes.json')) as f:
    filetypes = json.loads(f.read())
    for name, ext in filetypes.items():
        filetypes[name] = Path(ext)

with open(get_resource_path(Path('editor') / 'filetypes' / 'uncreatable.json')) as f:
    uncreatable_filetypes = json.loads(f.read())
    for name, ext in uncreatable_filetypes.items():
        uncreatable_filetypes[name] = Path(ext)


class FileIconProvider(QtWidgets.QFileIconProvider):
    def icon(self, file_info):
        if not hasattr(file_info, 'suffix'):
            return QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'file_icons' / 'folder.png')))
        if file_info.suffix() == '':
            return QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'file_icons' / 'folder.png')))
        else:
            for key, item in {**filetypes, **uncreatable_filetypes}.items():
                if file_info.suffix() == item.suffix:
                    return QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'file_icons' / (key + '.png'))))
            return QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'file_icons' / 'file.png')))


class FileSystem(QtWidgets.QTreeView):
    def __init__(self, editor, path):
        super().__init__()
        self.editor = editor
        self.path = path
        self.directory_model = QtWidgets.QFileSystemModel(self)
        self.directory_model.setRootPath('')
        self.directory_model.setIconProvider(FileIconProvider())
        self.root_index = self.directory_model.index(QtCore.QDir.cleanPath(str(self.path)))

        self.setModel(self.directory_model)
        self.setIndentation(20)
        self.setSortingEnabled(True)
        self.setColumnHidden(1, True)
        self.setColumnHidden(2, True)
        self.setColumnHidden(3, True)
        self.setRootIndex(self.root_index)

        self.create_file_action = QtGui.QAction('Create New', self)
        self.create_file_action.triggered.connect(self.create_new)
        self.create_directory_action = QtGui.QAction('Create Directory', self)
        self.create_directory_action.triggered.connect(self.create_folder)
        self.import_files_action = QtGui.QAction('Import Files', self)
        self.import_files_action.triggered.connect(self.import_asset)
        self.import_folder_action = QtGui.QAction('Import Folder', self)
        self.import_folder_action.triggered.connect(lambda: self.import_asset(dir=True))
        self.delete_action = QtGui.QAction('Delete', self)
        self.delete_action.triggered.connect(self.delete)

    def contextMenuEvent(self, event):
        if self.currentIndex() is None:
            self.delete_action.setEnabled(False)

        else:
            self.delete_action.setEnabled(True)

        context_menu = QtWidgets.QMenu(self)

        create_menu = context_menu.addMenu('Create')
        create_menu.addAction(self.create_file_action)
        create_menu.addAction(self.create_directory_action)

        import_menu = context_menu.addMenu('Import')
        import_menu.addAction(self.import_files_action)
        import_menu.addAction(self.import_folder_action)

        context_menu.addAction(self.delete_action)

        context_menu.exec(self.mapToGlobal(event.pos()))

    def get_append_path(self):
        if self.currentIndex():
            path = Path(self.directory_model.filePath(self.currentIndex()))
            if path.is_file():
                path = path.parent

        else:
            path = self.path

        return path

    def delete(self):
        path = Path(self.directory_model.filePath(self.currentIndex()))
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)

    def create_new(self):
        dialog = FiletypeSelectionDialog(self)
        code = dialog.exec()
        if code == QtWidgets.QDialog.DialogCode.Accepted:
            self.create_file(filetypes[dialog.filetype], dialog.filename)

    def create_file(self, filepath, name):
        path = self.get_append_path()

        if not path:
            return
        if not name:
            return

        path = path / (name + filepath.suffix)
        if not path.exists():
            shutil.copy(str(get_resource_path(Path('editor') / 'filetypes' / filepath)), path)

    def create_folder(self):
        dialog = TextSelectionDialog(self, 'Name of Directory', 'Name')
        code = dialog.exec()
        if code == QtWidgets.QDialog.DialogCode.Accepted:
            self.mkdir(dialog.input_text)

    def mkdir(self, name):
        path = self.get_append_path()

        path = path / name

        if not path.exists():
            path.mkdir()

    def import_asset(self, dir=False):
        path = self.get_append_path()
        if dir:
            files = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a directory", str(self.path), QtWidgets.QFileDialog.Option.ShowDirsOnly)
            if not files:
                return
            files = [Path(files)]
        else:
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(None, "Select one or more files", str(self.path), "All Files (*)")
            if not files:
                return
            files = [Path(f) for f in files]

        self.editor.task_manager.new_task('import_asset', [path, files])
