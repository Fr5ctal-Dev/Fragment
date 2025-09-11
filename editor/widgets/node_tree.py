
"""from PySide6 import QtWidgets, QtGui, QtCore


class NodeTree(QtWidgets.QTreeWidget):
    node_dragged_signal = QtCore.Signal(list, QtWidgets.QTreeWidgetItem) # Sources, Dest
    def __init__(self):
        super().__init__()
        self.setColumnCount(1)
        self.setHeaderLabels(['Name'])

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)

        self.set_root_action = QtGui.QAction('Set Root Node', self)
        self.new_node_action = QtGui.QAction('New Node', self)
        self.new_nested_scene_action = QtGui.QAction('New Scene', self)
        self.delete_node_action = QtGui.QAction('Delete', self)
        self.rename_node_action = QtGui.QAction('Rename', self)
        self.copy_id_action = QtGui.QAction('Copy ID', self)

        self.with_root = True

    def contextMenuEvent(self, event):
        if self.currentItem() is not None:
            self.itemClicked.emit(self.currentItem(), 0)

        context_menu = QtWidgets.QMenu(self)
        if self.with_root:
            self.set_root_action.setEnabled(False)
            self.new_node_action.setEnabled(True)
            self.new_nested_scene_action.setEnabled(True)
        else:
            self.set_root_action.setEnabled(True)
            self.new_node_action.setEnabled(False)
            self.new_nested_scene_action.setEnabled(False)

        if self.currentItem() is not None:
            self.delete_node_action.setEnabled(True)
            self.rename_node_action.setEnabled(True)
            self.copy_id_action.setEnabled(True)
        else:
            self.delete_node_action.setEnabled(False)
            self.rename_node_action.setEnabled(False)
            self.copy_id_action.setEnabled(False)

        new_menu = context_menu.addMenu('New')
        new_menu.addAction(self.new_node_action)
        new_menu.addAction(self.new_nested_scene_action)

        context_menu.addAction(self.delete_node_action)
        context_menu.addAction(self.rename_node_action)
        context_menu.addAction(self.set_root_action)
        context_menu.addAction(self.copy_id_action)

        context_menu.exec(self.mapToGlobal(event.pos()))

    def dragEnterEvent(self, event):
        if event.source() is self:
            event.accept()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        src = event.source()

        dragged_items = src.selectedItems()

        drop_pos = event.position().toPoint()
        dest_item = self.itemAt(drop_pos)

        self.node_dragged_signal.emit(dragged_items, dest_item)

        event.ignore()

    def insertTopLevelItem(self, index, item):
        super().insertTopLevelItem(index, item)
        self.with_root = True
"""

from editor.dialogs.new_node_selection import NewNodeSelectionDialog
from editor.utils.path import get_resource_path
from editor.node_properties.loader import tree as node_properties
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem, QAbstractItemView, QTreeWidgetItemIterator, QMessageBox, QMenu
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon, QAction
import copy


class NodeTree(QTreeWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.node_data = {} # {item: dict}

        self.setHeaderLabel('Node Tree')
        self.setEditTriggers(QAbstractItemView.EditTrigger.DoubleClicked)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.itemChanged.connect(self._on_item_changed)
        self._editing_item = None
        self._previous_name = None
        self.itemDoubleClicked.connect(self._on_item_double_clicked)

        self.new_node_action = QAction('New Node', self)
        self.new_node_action.triggered.connect(self.new_node_selection_dialog)
        self.delete_node_action = QAction('Delete Node', self)
        self.delete_node_action.triggered.connect(lambda: self.delete_node(self.currentItem()))

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        new_menu = context_menu.addMenu('New')
        new_menu.addAction(self.new_node_action)

        context_menu.addAction(self.delete_node_action)

        context_menu.exec(self.mapToGlobal(event.pos()))
    
    def new_node_selection_dialog(self):
        selection_dialog = NewNodeSelectionDialog(self)
        selection_dialog.accepted.connect(lambda: self.new_node(selection_dialog.node_name, selection_dialog.node_type, self.currentItem()))
        selection_dialog.exec()
    
    def new_node(self, name, type, parent=None, properties=None):
        item = QTreeWidgetItem()
        item.setText(0, name)
        item.setIcon(0, QIcon(get_resource_path(f'editor/assets/node_icons/{type}.png')))
        item.setFlags(item.flags() | Qt.ItemFlag.ItemIsEditable)
        
        if parent is None:
            root = self.topLevelItem(0)
            if root is not None:
                root.addChild(item)
                root.setExpanded(True)
            else:
                self.addTopLevelItem(item)
        else:
            parent.addChild(item)
            parent.setExpanded(True)
        
        if properties is None:
            properties = copy.deepcopy(node_properties[type])
        self.node_data[item] = {'type': type, 'properties': properties}

        return item
    
    def delete_node(self, item):
        if item is None:
            return
        
        self.node_data.pop(item)
        for decendent in self.dfs_children(item):
            self.node_data.pop(decendent)
        
        parent = item.parent()
        
        if parent is None:
            index = self.indexOfTopLevelItem(item)
            if index != -1:
                self.takeTopLevelItem(index)
        else:
            parent.removeChild(item)

    def dfs_children(self, item, items=None):
        if items is None: items = []
        for child_index in range(item.childCount()):
            child = item.child(child_index)
            items.append(child)
            self.dfs_children(child, items)
        return items
    
    def is_valid_name(self, item):
        name = item.text(0)
        if not name.strip():
            return False

        if item.parent() is not None:
            for sibling_index in range(item.parent().childCount()):
                sibling = item.parent().child(sibling_index)
                if sibling.text(0) == name and sibling != item:
                    QMessageBox.warning(self, 'Invalid Name', 'Node name must be unique within the same parent.')
                    return False

        return True
    
    def is_valid_reparent(self, source, target):
        if target is None:
            return False
        
        for sibling_index in range(target.childCount()):
            sibling = target.child(sibling_index)
            if sibling.text(0) == source.text(0) and sibling != source:
                QMessageBox.warning(self, 'Invalid Reparent', 'Node name must be unique within the same parent.')
                return False

        return True
    
    def dropEvent(self, event):
        source_item = self.currentItem()
        
        if source_item is None:
            event.ignore()
            return
        
        target_item = self.itemAt(event.position().toPoint())
        
        drop_indicator = self.dropIndicatorPosition()
        
        if target_item is None:
            target_parent = None
        elif drop_indicator == QAbstractItemView.DropIndicatorPosition.OnItem:
            target_parent = target_item
        elif drop_indicator == QAbstractItemView.DropIndicatorPosition.AboveItem or \
             drop_indicator == QAbstractItemView.DropIndicatorPosition.BelowItem:
            target_parent = target_item.parent()
        else:
            target_parent = None
        
        if not self.is_valid_reparent(source_item, target_parent):
            event.ignore()
            return
        
        super().dropEvent(event)
    
    def _on_item_double_clicked(self, item, column):
        self._editing_item = item
        self._previous_name = item.text(0) if item else None
    
    def _on_item_changed(self, item, column):
        if item != self._editing_item or column != 0:
            return
        
        if not self.is_valid_name(item):
            if self._previous_name is not None:
                item.setText(0, self._previous_name)
        
        self._editing_item = None
        self._previous_name = None

    def get_all_nodes(self):
        nodes = []
        iterator = QTreeWidgetItemIterator(self)
        
        while iterator.value():
            nodes.append(iterator.value())
            iterator += 1
        
        return nodes
    
    def path_of_node(self, item):
        path = [item.text(0)]
        current_item = item
        while True:
            if current_item.parent(): current_item = current_item.parent()
            else: return tuple(path)
            path.insert(0, current_item.text(0))
    
    def load_from_scene_data(self, data):
        '''
        Reference:
        data should look like this:
        {tuple_node_path: {type, properties, ...}}
        '''
        if self.node_data:
            self.delete_node(self.topLevelItem(0))
        
        temp_parent_storage = {}
        for path, node_data in data.items():
            parent = None if len(path) == 1 else temp_parent_storage[path[:-1]]
            temp_parent_storage[path] = self.new_node(path[-1], node_data['type'], parent, node_data['properties'])

    def save_to_scene_data(self):
        data = {}
        for node in self.get_all_nodes():
            data[self.path_of_node(node)] = self.node_data[node]
        return data
