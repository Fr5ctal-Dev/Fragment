from dialogs.filetype_selection import FiletypeSelectionDialog
from dialogs.text_selection import TextSelectionDialog

from PySide6 import QtWidgets, QtCore, QtGui

import json
import shutil
import os


fp = open('filetypes/filetypes.json')
filetypes = json.loads(fp.read())
fp.close()

fp = open('filetypes/uncreatable.json')
uncreatable_filetypes = json.loads(fp.read())
fp.close()


class FileIconProvider(QtWidgets.QFileIconProvider):
    def icon(self, file_info):
        if not hasattr(file_info, 'suffix'):
            return QtGui.QIcon('assets/file_icons/folder.png')
        if file_info.suffix() == '':
            return QtGui.QIcon('assets/file_icons/folder.png')
        else:
            for key, item in {**filetypes, **uncreatable_filetypes}.items():
                if file_info.suffix() == item.split('.')[-1]:
                    return QtGui.QIcon('assets/file_icons/' + key + '.png')
            return QtGui.QIcon('assets/file_icons/file.png')


class FileSystem(QtWidgets.QTreeView):
    def __init__(self, editor, path):
        super().__init__()
        self.editor = editor
        self.path = path
        self.directory_model = QtWidgets.QFileSystemModel(self)
        self.directory_model.setRootPath('')
        self.directory_model.setIconProvider(FileIconProvider())
        self.root_index = self.directory_model.index(QtCore.QDir.cleanPath(self.path))

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
            path = self.directory_model.filePath(self.currentIndex())
            if os.path.isfile(path):
                path = os.path.dirname(path)

        else:
            path = self.path

        return path

    def delete(self):
        path = self.directory_model.filePath(self.currentIndex())
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    def create_new(self):
        dialog = FiletypeSelectionDialog(self)
        dialog.accept_button.clicked.connect(lambda: (self.create_file(filetypes[dialog.filelist.currentItem().text()], dialog.name_edit.text()), dialog.accept()))
        dialog.exec()

    def create_file(self, filepath, name):
        path = self.get_append_path()

        if not path:
            return
        if not name:
            return

        path += '/' + name + '.' + filepath.split('.')[1]
        if not os.path.exists(path):
            shutil.copy(f'filetypes/{filepath}', path)

    def create_folder(self):
        dialog = TextSelectionDialog(self, 'Name of Directory', 'Name')
        dialog.accept_button.clicked.connect(lambda: (self.mkdir(dialog.line_edit.text()), dialog.accept()))
        dialog.exec()

    def mkdir(self, name):
        path = self.get_append_path()

        path += '/' + name

        if not os.path.exists(path):
            os.mkdir(path)

    def import_asset(self, dir=False):
        path = self.get_append_path()
        if dir:
            files = QtWidgets.QFileDialog.getExistingDirectory(None, "Select a directory", self.path, QtWidgets.QFileDialog.Option.ShowDirsOnly)
            if not files:
                return
            files = [files]
        else:
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(None, "Select one or more files", self.path, "All Files (*)")
            if not files:
                return

        self.editor.task_manager.new_task('import_asset', [path, files])
