from editor.dialogs.new_node_selection import NewNodeSelectionDialog
from editor.dialogs.file_selection import get_open_relative_file_name
from editor.utils.path import get_resource_path
from editor.node_properties.loader import node_properties as NODE_PROPERTIES
from editor.node_properties.nodes.base_node import BaseNodeProperties
from PySide6 import QtWidgets, QtGui, QtCore
from PySide6.QtCore import Qt
from uuid import uuid4
from pathlib import Path
import json


class NodeTree(QtWidgets.QTreeWidget):
    def __init__(self, scene_editor):
        super().__init__()
        self.scene_editor = scene_editor
        self.node_data = {} # {item: dict}

        self.setHeaderLabel('Node Tree')
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.DoubleClicked)
        self.setDragDropMode(QtWidgets.QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
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

        self.update_timer = QtCore.QTimer(self)
        self.update_timer.timeout.connect(self.update_scene_nodes)
        self.update_timer.start(10)

    def contextMenuEvent(self, event):
        context_menu = QtWidgets.QMenu(self)
        new_menu = context_menu.addMenu('New')
        new_menu.addAction(self.new_node_action)
        new_menu.addAction(self.new_scene_action)

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

    def new_node(self, type, parent=None, properties=None, uuid=None, name=None):
        uuid = uuid or str(uuid4())
        item = QtWidgets.QTreeWidgetItem()
        if name is not None:
            item.setText(0, name)
        elif properties is not None:
            item.setText(0, properties.properties['Node/Name'].value)
        else:
            item.setText(0, 'New Node')
        item.setIcon(0, QtGui.QIcon(str(get_resource_path(Path('editor') / 'assets' / 'node_icons' / f'{type}.png'))))
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
            properties = NODE_PROPERTIES[type](self.scene_editor, uuid, type)
            properties.set_property('Node/Name', name)
        self.node_data[item] = properties

        properties.uuid = uuid

        properties.properties['Node/Name'].value_changed.connect(lambda: item.setText(0, properties.properties['Node/Name'].value))

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
        if items is None:
            items = []
        for child_index in range(item.childCount()):
            child = item.child(child_index)
            items.append(child)
            self.dfs_children(child, items)
        return items
    
    def is_valid_name(self, item):
        return True
    
    def is_valid_reparent(self, source, target):
        if target is None:
            return False
        
        if self.node_data[source].target_scene is not None and len(self.node_data[source].target_scene_node) > 1:
            QtWidgets.QMessageBox.warning(self, 'Invalid Operation', 'Cannot reparent a child node of an imported scene.')
            return False
        
        if self.node_data[target].target_scene is not None:
            QtWidgets.QMessageBox.warning(self, 'Invalid Operation', 'Cannot reparent to an imported scene node.')
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
        elif drop_indicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.OnItem:
            target_parent = target_item
        elif drop_indicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.AboveItem or \
             drop_indicator == QtWidgets.QAbstractItemView.DropIndicatorPosition.BelowItem:
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
                self.rename_node(item, self._previous_name)
        else:
            self.rename_node(item, item.text(0))
        
        self._editing_item = None
        self._previous_name = None

    def rename_node(self, item, new_name):
        item.setText(0, new_name)
        self.node_data[item].set_property('Node/Name', new_name)

    def get_all_nodes(self):
        nodes = []
        iterator = QtWidgets.QTreeWidgetItemIterator(self)
        
        while iterator.value():
            nodes.append(iterator.value())
            iterator += 1
        
        return nodes
    
    def path_of_node(self, item):
        path = [self.node_data[item].uuid]
        current_item = item
        while True:
            if current_item.parent():
                current_item = current_item.parent()
            else:
                return tuple(path)
            path.insert(0, self.node_data[current_item].uuid)
    
    def node_properties_to_data(self, node_properties: BaseNodeProperties): # The node properties class
        return node_properties.to_data()

    def data_to_node_properties(self, data, name):
        type = data['type']
        properties = NODE_PROPERTIES[type](self.scene_editor, name, type)
        properties.load_data(data)
        return properties
    
    def load_from_scene_data(self, data):
        if self.node_data:
            self.delete_node(self.topLevelItem(0))

        temp_parent_storage = {}
        for path, node_data in data.items():
            parent = None if len(path) == 1 else temp_parent_storage[path[:-1]]
            temp_parent_storage[path] = self.new_node(node_data['type'], parent, self.data_to_node_properties(node_data, path[-1]), uuid=path[-1])

    def save_to_scene_data(self):
        data = {}
        for node in self.get_all_nodes():
            properties = self.node_data[node]
            path = self.path_of_node(node)
            data[path] = self.node_properties_to_data(properties)

            # Store parent and uuid for js runtime
            data[path]['parent'] = json.dumps(self.path_of_node(node.parent())) if node.parent() else None
            data[path]['uuid'] = properties.uuid
        return data
    
    def node_selected(self, item):
        inspector = self.scene_editor.inspector
        if item in self.node_data:
            inspector.set_inspector(self.node_data[item].property_tree)

    def load_scene(self, scene_path, parent=None):
        if scene_path == self.scene_editor.scene:
            QtWidgets.QMessageBox.warning(self, 'Invalid Operation', 'Cannot import the current scene into itself.')
            return

        with open(self.scene_editor.path / scene_path) as f:
            content = json.load(f)

        data = {}
        for json_key, node_data in content.items():
            path_list = json.loads(json_key)
            data[tuple(path_list)] = node_data

        temp_parent_storage = {}
        for path, node_data in data.items():
            for prop_value in node_data['properties'].values():
                prop_value['scene_override'] = False

            parent = parent if len(path) == 1 else temp_parent_storage[path[:-1]]
            node = self.new_node(node_data['type'], parent, self.data_to_node_properties(node_data, path[-1]))
            temp_parent_storage[path] = node

            if node is not None:
                self.node_data[node].connect_scene(scene_path, path)
            else:
                return

    def get_all_scene_root_nodes(self):
        root_nodes = []
        for node in self.get_all_nodes():
            properties = self.node_data[node]
            if properties.target_scene and len(properties.target_scene_node) == 1:
                root_nodes.append(node)
        return root_nodes
    
    def handle_scene_change(self, scene, root_node):
        with open(self.scene_editor.path / scene) as f:
            content = json.load(f)

        data = {}
        for json_key, node_data in content.items():
            path_list = json.loads(json_key)
            data[tuple(path_list)] = node_data

        root_deleted = False
        root_parent = root_node.parent()
        
        # Compare current to other scene
        for node in [root_node] + self.dfs_children(root_node):
            node_property = self.node_data.get(node)
            if node_property is None: # Node has been deleted
                continue
            if node_property.target_scene == scene:
                if node_property.target_scene_node in data and node_property.type == data[node_property.target_scene_node]['type']:
                    continue
                self.delete_node(node)
                if node == root_node:
                    root_deleted = True
                    break

        # Compare other scene to current
        if root_deleted:
            temp_parent_storage = {}
            for path, node_data in data.items():
                temp_parent_storage[path] = self.new_node(node_data['type'], temp_parent_storage.get(path[:-1]) or root_parent, self.data_to_node_properties(node_data, path[-1]), uuid=path[-1])
                self.node_data[temp_parent_storage[path]].connect_scene(scene, path)

        else:
            current_scene_nodes = {} # {relative_path: node}

            for node in [root_node] + self.dfs_children(root_node):
                if self.node_data[node].target_scene == scene:
                    current_scene_nodes[self.node_data[node].target_scene_node] = node
            for path, node_data in data.items():
                if path in current_scene_nodes and self.node_data[current_scene_nodes[path]].type == node_data['type']:
                    continue
                current_scene_nodes[path] = self.new_node(node_data['type'], current_scene_nodes.get(path[:-1]), self.data_to_node_properties(node_data, path[-1]), uuid=path[-1])
                self.node_data[current_scene_nodes[path]].connect_scene(scene, path)

    def update_scene_nodes(self):
        # Check for changed scenes
        for root_node in self.get_all_scene_root_nodes():
            self.handle_scene_change(self.node_data[root_node].target_scene, root_node)

        # Update properties
        for node in self.get_all_nodes():
            properties = self.node_data[node]
            properties.update_scene_properties()

    def cleanup(self):
        self.update_timer.stop()
