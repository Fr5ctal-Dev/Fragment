from PySide6.QtCore import Signal
from editor.core.models.properties import PropertiesModel
from editor.ui.views.nodes.property import NodePropertyView
from pathlib import Path
import json


class BaseNodeProperties(PropertiesModel):
    name_changed = Signal()
    recommended_view = NodePropertyView
    def __init__(self, scene_editor, uuid, type):
        super().__init__()
        self.scene_editor = scene_editor
        self.type = type
        self.uuid = uuid

        self.target_scene = None # Scene path
        self.target_scene_node = None # Node path in target scene

    @property
    def default_properties(self):
        properties = {} # name: property
        return properties
    
    def set_property(self, name, value):
        self.properties[name].value = value

    def override_property(self, name):
        self.properties[name].scene_override = True
    
    def unoverride_property(self, name):
        self.properties[name].scene_override = False

    def setup_property_editors(self):
        for prop in self.properties.values():
            prop.setup_property_editor(self.scene_editor)

    def to_data(self):
        data = {'type': self.type, 'properties': {}}

        data['target_scene'] = self.target_scene.as_posix() if self.target_scene else None
        data['target_scene_node'] = self.target_scene_node

        for name, property in self.properties.items():
            data['properties'][name] = property.to_data()
        return data
    
    def load_data(self, data):
        for name, property in data['properties'].items():
            self.set_property(name, property['value'])
            if property['scene_override']:
                self.override_property(name)

        if 'target_scene' in data and data['target_scene'] is not None:
            self.connect_scene(Path(data['target_scene']), data['target_scene_node'])

    def connect_scene(self, scene_path, node_path):
        self.target_scene = scene_path
        self.target_scene_node = tuple(node_path)

    def update_scene_properties(self):
        if self.target_scene and self.target_scene_node:
            with open(self.scene_editor.path / self.target_scene) as f:
                content = json.load(f)

            data = {}
            for json_key, node_data in content.items():
                path_list = json.loads(json_key)
                data[tuple(path_list)] = node_data

            if self.target_scene_node in data:
                node_data = data[self.target_scene_node]
                for name, property in node_data['properties'].items():
                    if name in self.properties and not self.properties[name].scene_override:
                        self.set_property(name, property['value'])
