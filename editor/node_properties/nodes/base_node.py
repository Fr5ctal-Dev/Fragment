from PySide6 import QtWidgets


class BaseNodeProperties:
    def __init__(self, scene_editor, uuid, type):
        self.scene_editor = scene_editor
        self.type = type
        self.uuid = uuid

        self.target_scene = None # Scene path
        self.target_scene_node = None # Node path in target scene

        self.properties = self.default_properties
        self.property_tree = None
        self.setup_property_tree()

    @property
    def default_properties(self):
        properties = {} # name: property
        return properties
    
    def set_property(self, name, value):
        self.properties[name].value = value

    def setup_property_tree(self):
        self.setup_property_editors()
        self.property_tree = QtWidgets.QTreeWidget()
        self.property_tree.setColumnCount(2)
        self.property_tree.setHeaderLabels(['Name', 'Value'])
        self.property_tree.setIndentation(15)

        for prop in self.properties.values():
            item = QtWidgets.QTreeWidgetItem([prop.name, ''])
            self.property_tree.addTopLevelItem(item)
            self.property_tree.setItemWidget(item, 1, prop.editor_widget)

    def setup_property_editors(self):
        for prop in self.properties.values():
            prop.setup_property_editor(self.scene_editor, self.type)

    def to_data(self):
        data = {'type': self.type, 'properties': {}}

        if self.target_scene:
            data['target_scene'] = self.target_scene
            data['target_scene_node'] = self.target_scene_node

        for name, property in self.properties.items():
            data['properties'][name] = property.to_data()
        return data
    
    def load_data(self, data):
        for name, property in data['properties'].items():
            self.set_property(name, property['value'])

        if 'target_scene' in data:
            self.connect_scene(data['target_scene'], data['target_scene_node'])

    def connect_scene(self, scene_path, node_path):
        self.target_scene = scene_path
        self.target_scene_node = node_path

    def update_scene_properties(self):
        if self.target_scene and self.target_scene_node:
            with open(self.target_scene) as f:
                data = f.read()
            data = eval(data)

            if self.target_scene_node in data:
                node_data = data[self.target_scene_node]
                for name, property in node_data['properties'].items():
                    if name in self.properties:
                        self.set_property(name, property['value'])
