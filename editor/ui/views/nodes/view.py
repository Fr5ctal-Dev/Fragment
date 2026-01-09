from editor.ui.dialogs.new_node_selection import NewNodeSelectionDialog
from editor.ui.dialogs.file_selection import get_open_relative_file_name
from editor.core.models.nodes import NodeTreeModel
from editor.core.models.nodes.node_item import NodeItem
from editor.tools.utils.path import get_resource_path
from ..base_view import BaseView
from PySide6 import QtWidgets, QtGui
from PySide6.QtCore import Qt
from pathlib import Path


class NodeView(BaseView):
    def __init__(self, editor, scene_editor):
        super().__init__(editor)
        self.scene_editor = scene_editor
        self.node_tree = None

    def cleanup(self):
        super().cleanup()
        if self.node_tree:
            self.node_tree.cleanup()
            self.node_tree.deleteLater()
            self.node_tree = None

    def display(self):
        assert self.model is not None # For type checker
        self.node_tree = NodeTree(self.scene_editor, self.model)


class NodeTree(QtWidgets.QTreeWidget):
    def __init__(self, scene_editor, model: NodeTreeModel):
        super().__init__()
        self.scene_editor = scene_editor
        self.tree_model = model

        self.tree_item_map: dict[QtWidgets.QTreeWidgetItem, NodeItem] = {}

        self.setHeaderLabel('Node Tree')
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setExpandsOnDoubleClick(False)

        self.itemChanged.connect(self._on_item_changed)
        self._editing_item = None
        self._previous_name = None
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.itemSelectionChanged.connect(lambda: self.node_selected(self.currentItem()))

        self.new_node_action = QtGui.QAction('New Node', self)
        self.new_node_action.triggered.connect(self.new_node_selection_dialog)
        self.new_scene_action = QtGui.QAction('New Scene', self)
        self.new_scene_action.triggered.connect(self.new_scene_selection)
        self.delete_node_action = QtGui.QAction('Delete Node', self)
        self.delete_node_action.triggered.connect(lambda: self.delete_node(self.currentItem()))

        self.tree_model.node_created.connect(self.new_item)
        self.tree_model.node_deleted.connect(self.delete_item)
        self.tree_model.node_renamed.connect(self.rename_item)
        self.tree_model.node_reparented.connect(self.reparent_item)
        self.tree_model.error.connect(self.error_message)

        self.init_nodes()

    def init_nodes(self):
        for node in self.tree_model.node_data.keys():
            self.new_item(node)

    def error_message(self, message):
        QtWidgets.QMessageBox.warning(self, 'Error', message)

    @property
    def tree_item_inverse_map(self) -> dict[NodeItem, QtWidgets.QTreeWidgetItem]:
        return {v: k for k, v in self.tree_item_map.items()}

    def contextMenuEvent(self, event):
        context_menu = QtWidgets.QMenu(self)
        new_menu = context_menu.addMenu('New')
        new_menu.addAction(self.new_node_action)
        new_menu.addAction(self.new_scene_action)

        if self.currentItem() is not None:
            self.delete_node_action.setEnabled(True)
        else:
            self.delete_node_action.setEnabled(False)
            
        context_menu.addAction(self.delete_node_action)

        context_menu.exec(self.mapToGlobal(event.pos()))
    
    def new_node_selection_dialog(self):
        selection_dialog = NewNodeSelectionDialog(self)
        code = selection_dialog.exec()
        if code == QtWidgets.QDialog.DialogCode.Accepted:
            self.new_node(selection_dialog.node_type, self.currentItem(), name=selection_dialog.node_name)

    def new_scene_selection(self):
        path = get_open_relative_file_name(self, self.scene_editor.path, 'Open Scene', 'Fragment Scenes (*.fscene)')
        if path:
            self.load_scene(Path(path), self.currentItem())
    
    def dropEvent(self, event):
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
            self.tree_model.reparent_node(self.tree_item_map[source_item], self.tree_item_map[target_parent])

        event.ignore()
    
    def node_selected(self, item):
        self.scene_editor.editor.set_inspector_model(self.tree_model.node_data[self.tree_item_map[item]] if item else None)

    def reparent_node(self, item: QtWidgets.QTreeWidgetItem, parent: QtWidgets.QTreeWidgetItem):
        self.tree_model.reparent_node(self.tree_item_map[item], self.tree_item_map[parent])

    def delete_node(self, item: QtWidgets.QTreeWidgetItem):
        self.tree_model.delete_node(self.tree_item_map[item])

    def rename_node(self, item: QtWidgets.QTreeWidgetItem, new_name: str):
        self.tree_model.rename_node(self.tree_item_map[item], new_name)

    def load_scene(self, scene_path, parent: QtWidgets.QTreeWidgetItem | None = None):
        if parent:
            self.tree_model.load_scene(scene_path, self.tree_item_map[parent])
        else:
            self.tree_model.load_scene(scene_path, None)

    def new_node(self, node_type, parent_item=None, data=None, uuid=None, name=None):
        self.tree_model.new_node(node_type, self.tree_item_map[parent_item] if parent_item else None, data, uuid, name)

    def reparent_item(self, item: NodeItem, new_parent: NodeItem):
        self.tree_item_inverse_map[item].parent().removeChild(self.tree_item_inverse_map[item])
        self.tree_item_inverse_map[new_parent].addChild(self.tree_item_inverse_map[item])

    def delete_item(self, item: NodeItem):
        parent = self.tree_item_inverse_map[item].parent()
        if parent:
            parent.removeChild(self.tree_item_inverse_map[item])
        else:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.tree_item_inverse_map[item]))
    
    def rename_item(self, item: NodeItem, new_name: str):
        self.tree_item_inverse_map[item].setText(0, new_name)

    def new_item(self, node: NodeItem):
        tree_item = QtWidgets.QTreeWidgetItem()
        tree_item.setText(0, self.tree_model.node_data[node].properties['Node/Name'].value)
        tree_item.setIcon(0, QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'icons' / 'node' / f'{self.tree_model.node_data[node].type.lower()}.svg'))))
        tree_item.setFlags(tree_item.flags() | Qt.ItemFlag.ItemIsEditable)
        if node.parent:
            parent_item = self.tree_item_inverse_map[node.parent]
            parent_item.addChild(tree_item)
        else:
            self.addTopLevelItem(tree_item)
        self.tree_item_map[tree_item] = node

    def _on_item_double_clicked(self, item, column):
        self._editing_item = item
        self._previous_name = item.text(column) if item else None

    def _on_item_changed(self, item, column):
        if item != self._editing_item or column != 0:
            return
        self.rename_node(item, item.text(0))

        self._editing_item = None
        self._previous_name = None

    def cleanup(self):
        self.tree_model.node_created.disconnect(self.new_item)
        self.tree_model.node_deleted.disconnect(self.delete_item)
        self.tree_model.node_renamed.disconnect(self.rename_item)
        self.tree_model.node_reparented.disconnect(self.reparent_item)
        self.tree_model.error.disconnect(self.error_message)
        self.tree_item_map.clear()
