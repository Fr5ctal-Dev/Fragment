# Please rewrite this file when you decide to create a custom file selection dialog.
# This file is currently just a wrapper around the native file dialog but with relative paths.

from PySide6 import QtWidgets
from pathlib import Path

def get_open_relative_file_name(parent, relative_to: Path, caption='Open File', filter='') -> Path | None:
    path = QtWidgets.QFileDialog.getOpenFileName(parent, caption, str(relative_to), filter)[0]
    if not path:
        return None
    
    path = Path(path)
    if path.is_relative_to(relative_to):
        return path.relative_to(relative_to)
    else:
        QtWidgets.QMessageBox.warning(parent, 'Invalid path', f'Selected file is not relative to {relative_to}')
        return None

def get_save_relative_file_name(parent, relative_to: Path, caption='Save File', filter='') -> Path | None:
    path = QtWidgets.QFileDialog.getSaveFileName(parent, caption, str(relative_to), filter)[0]
    if not path:
        return None
    
    path = Path(path)
    if path.is_relative_to(relative_to):
        return path.relative_to(relative_to)
    else:
        QtWidgets.QMessageBox.warning(parent, 'Invalid path', f'Saved file is not relative to {relative_to}')
        return None
    
def get_open_relative_folder_name(parent, relative_to: Path, caption='Open Folder') -> Path | None:
    path = QtWidgets.QFileDialog.getExistingDirectory(parent, caption, str(relative_to))
    if not path:
        return None
    
    path = Path(path)
    if path.is_relative_to(relative_to):
        return path.relative_to(relative_to)
    else:
        QtWidgets.QMessageBox.warning(parent, 'Invalid path', f'Selected folder is not relative to {relative_to}')
        return None
