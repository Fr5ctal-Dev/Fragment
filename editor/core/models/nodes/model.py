from editor.core.models.base_model import BaseModel
from editor.core.models.nodes.loader import node_properties as NODE_PROPERTIES
from editor.core.models.nodes.nodes.base_node import BaseNodeProperties
from editor.tools.utils.node import NodeItem
from PySide6.QtCore import Signal, QTimer
from uuid import uuid4
import json


class NodeTreeModel(BaseModel):

    node_created = Signal(NodeItem)
    node_deleted = Signal(NodeItem)
    node_renamed = Signal(NodeItem, str)
    node_reparented = Signal(NodeItem, NodeItem) # item, new
    error = Signal(str)

    def __init__(self, scene_editor):
        super().__init__()
        self.scene_editor = scene_editor
        self.node_data: dict[NodeItem, BaseNodeProperties] = {}
        self.root_node: NodeItem | None = None
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_scene_nodes)
        self.update_timer.start(100) # Consider using threading for better performance

    def new_node(self, type, parent=None, data=None, uuid=None, name=None):
        uuid = uuid or str(uuid4())
        name = name if name is not None else type

        item = NodeItem()
        
        if parent is None:
            if self.root_node is None:
                self.root_node = item
            else:
                item.reparent(self.root_node)
        else:
            item.reparent(parent)
            
        properties = NODE_PROPERTIES[type](self.scene_editor, uuid, type)

        if data is None:
            properties.set_property('Node/Name', name)
        else:
            properties.load_data(data)
        properties.name_changed.connect(lambda: self.node_renamed.emit(item, properties.properties['Node/Name'].value))
        self.node_data[item] = properties

        self.node_created.emit(item)

        return item
    
    def delete_node(self, item: NodeItem):
        if self.node_data.get(item) is None:
            return
        
        self.node_data.pop(item)
        for decendent in self.dfs_children(item):
            self.node_data[decendent].cleanup()
            self.node_data.pop(decendent)
        
        parent = item.parent
        
        if parent is None:
            self.root_node = None
        else:
            item.reparent(None)

        self.node_deleted.emit(item)

    def dfs_children(self, item: NodeItem, items=None):
        if items is None:
            items = []
        for child in item.children:
            items.append(child)
            self.dfs_children(child, items)
        return items

    def rename_node(self, item: NodeItem, new_name):
        self.node_data[item].set_property('Node/Name', new_name)  # Rename node will be emitted from this

    def reparent_node(self, item: NodeItem, parent: NodeItem):
        if self.is_ancestor(item, parent):
            self.error.emit('Cannot reparent a node to its descendant.')
            return
        node_data = self.node_data[item]
        if (node_data.target_scene_node is not None) and len(node_data.target_scene_node) > 1:
            self.error.emit('Cannot reparent a scene node.')
            return

        item.reparent(parent)
        self.node_reparented.emit(item, parent)

    def get_all_nodes(self) -> list[NodeItem]:
        nodes = self.dfs_children(self.root_node) if self.root_node else []
        if self.root_node:
            nodes.insert(0, self.root_node)
        return nodes
    
    def path_of_node(self, item: NodeItem):
        path = [self.node_data[item].uuid]
        current_item = item
        while True:
            if current_item.parent:
                current_item = current_item.parent
            else:
                return tuple(path)
            path.insert(0, self.node_data[current_item].uuid)

    def is_ancestor(self, ancestor, descendant):
        current_item = descendant
        while current_item is not None:
            if current_item == ancestor:
                return True
            current_item = current_item.parent
        return False
    
    def node_properties_to_data(self, node_properties: BaseNodeProperties): # The node properties class
        return node_properties.to_data()
    
    def load_from_scene_data(self, data):
        if self.root_node:
            self.delete_node(self.root_node)

        temp_parent_storage = {}
        for path, node_data in data.items():
            parent = None if len(path) == 1 else temp_parent_storage[path[:-1]]
            temp_parent_storage[path] = self.new_node(node_data['type'], parent, node_data, path[-1])

    def save_to_scene_data(self):
        data = {}
        for node in self.get_all_nodes():
            properties = self.node_data[node]
            path = self.path_of_node(node)
            data[path] = self.node_properties_to_data(properties)

            # Store parent and uuid for js runtime
            data[path]['parent'] = json.dumps(self.path_of_node(node.parent)) if node.parent else None
            data[path]['uuid'] = properties.uuid
        return data

    def load_scene(self, scene_path, parent=None):
        if self.scene_editor.scene == scene_path:
            self.error.emit('Cannot load a scene into itself.')
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
            node = self.new_node(node_data['type'], parent, node_data) # UUID must be new to avoid conflicts across scene instances
            temp_parent_storage[path] = node

            if node is not None:
                self.node_data[node].connect_scene(scene_path, path)
            else:
                return

    def get_all_scene_root_nodes(self) -> list[NodeItem]:
        root_nodes = []
        for node in self.get_all_nodes():
            properties = self.node_data[node]
            if properties.target_scene_node and len(properties.target_scene_node) == 1:
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
        root_parent: NodeItem | None = root_node.parent
        
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
                temp_parent_storage[path] = self.new_node(node_data['type'], temp_parent_storage.get(path[:-1]) or root_parent, node_data) # UUID must be new to avoid conflicts across scene instances
                self.node_data[temp_parent_storage[path]].connect_scene(scene, path)

        else:
            current_scene_nodes = {} # {relative_path: node}

            for node in [root_node] + self.dfs_children(root_node):
                if self.node_data[node].target_scene == scene:
                    current_scene_nodes[self.node_data[node].target_scene_node] = node
            for path, node_data in data.items():
                if path in current_scene_nodes and self.node_data[current_scene_nodes[path]].type == node_data['type']:
                    continue
                current_scene_nodes[path] = self.new_node(node_data['type'], current_scene_nodes.get(path[:-1]), node_data) # UUID must be new to avoid conflicts across scene instances
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
        self.update_timer.deleteLater()
        for node_data in self.node_data.values():
            node_data.cleanup()
        super().cleanup()
