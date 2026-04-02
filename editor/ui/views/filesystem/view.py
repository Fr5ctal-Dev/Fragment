from ..base_view import BaseView
from editor.ui.dialogs.new_file_dialog import NewFileDialog
from editor.ui.dialogs.new_scene_dialog import NewSceneDialog
from editor.ui.dialogs.new_script_dialog import NewScriptDialog
from editor.ui.dialogs.file_rename_dialog import FileRenameDialog
from editor.core.models.filesystem import FileSystemModel
from editor.core.models.filesystem import FileNode
from editor.tools.utils.path import get_resource_path
from PySide6 import QtWidgets, QtGui
from pathlib import Path
import pyperclip



class FileSystemView(BaseView):
    def __init__(self, editor):
        super().__init__(editor)
        self.filesystem_tree = None

    def cleanup(self):
        super().cleanup()
        if self.filesystem_tree:
            self.filesystem_tree.cleanup()
            self.filesystem_tree.deleteLater()
            self.filesystem_tree = None

    def display(self):
        assert self.model is not None # For type checker
        self.filesystem_tree = FileSystemTree(self.editor, self.model)


class FileSystemTree(QtWidgets.QTreeWidget):
    def __init__(self, editor, model: FileSystemModel):
        super().__init__()
        self.editor = editor
        self.filesystem_model = model

        self.file_item_map: dict[QtWidgets.QTreeWidgetItem, FileNode] = {}
        self.file_item_inverse_map: dict[FileNode, QtWidgets.QTreeWidgetItem] = {}

        self.setHeaderLabel('File System')
        self.setIndentation(20)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)

        self.init_file_tree()
        
        self.filesystem_model.path_created.connect(self.new_item)
        self.filesystem_model.path_renamed.connect(self.rename_item)
        self.filesystem_model.path_deleted.connect(self.delete_item)
        self.filesystem_model.path_moved.connect(self.move_item)

        self.itemSelectionChanged.connect(lambda: self.on_item_selection_change(self.currentItem()))
        self.itemDoubleClicked.connect(self.open_item_file)

        self.delete_file_action = QtGui.QAction('Delete File', self)
        self.delete_file_action.triggered.connect(lambda: self.delete_file(self.currentItem()))

        self.copy_file_path_action = QtGui.QAction('Copy Path', self)
        self.copy_file_path_action.triggered.connect(lambda: self.copy_file_path(self.currentItem()))
        self.copy_relative_file_path_action = QtGui.QAction('Copy Relative Path', self)
        self.copy_relative_file_path_action.triggered.connect(lambda: self.copy_relative_file_path(self.currentItem()))

        self.new_file_action = QtGui.QAction('File', self)
        self.new_file_action.triggered.connect(lambda: self.new_file(self.currentItem()))

        self.new_script_file_action = QtGui.QAction('Script', self)
        self.new_script_file_action.triggered.connect(lambda: self.new_script_file(self.currentItem()))

        self.new_scene_file_action = QtGui.QAction('Scene', self)
        self.new_scene_file_action.triggered.connect(lambda: self.new_scene_file(self.currentItem()))

        self.rename_file_action = QtGui.QAction('Rename', self)
        self.rename_file_action.triggered.connect(lambda: self.rename_file(self.currentItem()))

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        if self.currentItem() is not None:
            menu.addAction(self.delete_file_action)
            menu.addSeparator()
            menu.addAction(self.copy_file_path_action)
            menu.addAction(self.copy_relative_file_path_action)

        if (self.filesystem_model.directory / self.file_item_map[self.currentItem()].get_path()).is_dir():
            menu.addSeparator()
            new_menu = menu.addMenu('New')
            new_menu.addAction(self.new_file_action)
            new_menu.addAction(self.new_script_file_action)
            new_menu.addAction(self.new_scene_file_action)
            
        menu.addSeparator()
        menu.addAction(self.rename_file_action)
        menu.exec(event.globalPos())

    def dropEvent(self, event: QtGui.QDropEvent):
        source_item = self.currentItem()
        
        if source_item is None:
            event.ignore()
            return
        
        target_item = self.itemAt(event.position().toPoint())
        
        drop_indicator = self.dropIndicatorPosition()
        
        if target_item is None:
            target_parent = None
        elif drop_indicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:
            target_parent = target_item
        elif drop_indicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem or \
             drop_indicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem:
            target_parent = target_item.parent()
        else:
            target_parent = None
        if target_parent:
            self.move_file(source_item, target_parent)
        event.ignore()

    def init_file_tree(self):
        root_node = self.filesystem_model.root_file_node
        assert root_node is not None
        #self.new_item(root_node)
        for child in root_node.dfs_children():
            self.new_item(child)

    def dfs_children(self, item: QtWidgets.QTreeWidgetItem) -> list[QtWidgets.QTreeWidgetItem]:
        result = []
        for child in [item.child(i) for i in range(item.childCount())]:
            result.append(child)
            result.extend(self.dfs_children(child))
        return result

    def new_item(self, filenode: FileNode):
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, filenode.name)
        item.setIcon(0, QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'file' / 'file.svg'))))

        self.file_item_map[item] = filenode
        self.file_item_inverse_map[filenode] = item

        parent_node = filenode.parent
        assert parent_node is not None
        if parent_node.parent is None: # Root node
            self.addTopLevelItem(item)
        else:
            parent_item = self.file_item_inverse_map[parent_node]
            parent_item.addChild(item)

    def rename_item(self, path: FileNode, name: str):
        item = self.file_item_inverse_map[path]
        item.setText(0, name)

    def delete_item(self, path: FileNode):
        item = self.file_item_inverse_map[path]
        parent_item = item.parent()
        if parent_item is None: # Root node
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
        else:
            parent_item.removeChild(item)

        for child in self.dfs_children(item):
            self.file_item_inverse_map.pop(self.file_item_map.pop(child))
        self.file_item_map.pop(item)
        self.file_item_inverse_map.pop(path)

    def move_item(self, old_path: FileNode, new_parent: FileNode):
        item = self.file_item_inverse_map[old_path]
        old_parent_item = item.parent()
        new_parent_item = self.file_item_inverse_map[new_parent]
        assert old_parent_item is not None # Root node cannot be moved
        old_parent_item.removeChild(item)
        new_parent_item.addChild(item)

    def on_item_selection_change(self, item: QtWidgets.QTreeWidgetItem):
        if item is None:
            self.editor.set_inspector_model(None)
            return
        self.editor.set_inspector_model(self.file_item_map[item].file_properties)

    def open_item_file(self, item: QtWidgets.QTreeWidgetItem, _):
        filenode = self.file_item_map[item]
        self.editor.open(filenode.get_path())

    def copy_file_path(self, item: QtWidgets.QTreeWidgetItem):
        filenode = self.file_item_map[item]
        path = self.filesystem_model.directory / filenode.get_path()
        pyperclip.copy(str(path))

    def copy_relative_file_path(self, item: QtWidgets.QTreeWidgetItem):
        filenode = self.file_item_map[item]
        path = filenode.get_path()
        pyperclip.copy(str(path))

    def delete_file(self, item: QtWidgets.QTreeWidgetItem):
        filenode = self.file_item_map[item]
        self.filesystem_model.delete_path(filenode)

    def new_file(self, parent_item: QtWidgets.QTreeWidgetItem):
        dialog = NewFileDialog(self.editor)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            file_name = dialog.file_name
            self.filesystem_model.new_file(self.file_item_map[parent_item].get_path() / file_name)

    def new_scene_file(self, parent_item: QtWidgets.QTreeWidgetItem):
        dialog = NewSceneDialog(self.editor)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            scene_name = dialog.scene_name
            self.filesystem_model.new_scene_file(self.file_item_map[parent_item].get_path() / scene_name)

    def new_script_file(self, parent_item: QtWidgets.QTreeWidgetItem):
        dialog = NewScriptDialog(self.editor)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            script_name = dialog.script_name
            self.filesystem_model.new_script_file(self.file_item_map[parent_item].get_path() / script_name)

    def rename_file(self, item: QtWidgets.QTreeWidgetItem):
        dialog = FileRenameDialog(self.editor)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            new_name = dialog.file_name
            self.filesystem_model.rename_path(self.file_item_map[item], new_name)

    def move_file(self, item: QtWidgets.QTreeWidgetItem, new_parent: QtWidgets.QTreeWidgetItem):
        new_parent_node = self.file_item_map[new_parent]
        if not new_parent_node.get_path().is_dir():
            QtWidgets.QMessageBox.warning(self, 'Invalid Move', 'Cannot move a file into another file.')
            return
        curr_parent = new_parent
        while curr_parent is not None:
            if curr_parent == item:
                QtWidgets.QMessageBox.warning(self, 'Invalid Move', 'Cannot move a folder into itself or its subfolder.')
                return
            curr_parent = curr_parent.parent()
        filenode = self.file_item_map[item]
        new_parent_node = self.file_item_map[new_parent]
        self.filesystem_model.move_path(filenode, new_parent_node)

    def cleanup(self):
        self.file_item_map.clear()
        self.file_item_inverse_map.clear()
