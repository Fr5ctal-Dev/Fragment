from .manager import Manager
from ..nodes import NODES
import importlib
import json
from pathlib import Path

with open('fragment/nodes/name_ref.json') as f:
    content = json.loads(f.read())

PROPERTY_NAME_REFERENCE = {}
for value in list(content.values()):
    PROPERTY_NAME_REFERENCE = {**PROPERTY_NAME_REFERENCE, **value}

class Scene(Manager):
    def __init__(self, game_manager, scene):
        super().__init__(game_manager)
        self.project_path = self.game_manager.project_path
        self.scene = scene
        self.root_node = None

        self.node_storage = [] # So you don't need to DFS the node tree every frame
        self.init()

    def init(self):
        with open(self.scene) as f:
            scene_content = f.read()
        scene_content = eval(scene_content)
        if not scene_content:
            return

        temp_node_storage = {}

        for node_path in list(scene_content.keys()):
            properties = {}
            for value in scene_content[node_path]['properties'].values():
                properties = {**properties, **value}

            if properties['script']:
                path = Path(properties['script']).relative_to(self.project_path)
                module = '.'.join(path.with_suffix('').parts)
                node_class = getattr(importlib.import_module(module), 'Node')
            else:
                node_class = NODES[scene_content[node_path]['type']]

            node = node_class(self.game_manager, self.convert_node_properties(properties))
            node.name = scene_content[node_path]['name']
            node.uuid = scene_content[node_path]['uid']

            if scene_content[node_path]['parent']:
                node.set_parent(temp_node_storage[scene_content[node_path]['parent']])
            else:
                self.root_node = node

            temp_node_storage[node_path] = node
            self.register_node(node)

        for node in temp_node_storage.values():
            node.on_start()

    def register_node(self, node):
        self.node_storage.append(node)

    def convert_node_properties(self, properties):
        new_properties = {}
        for key in list(properties.keys()):
            if PROPERTY_NAME_REFERENCE[key] is not None:
                new_properties[PROPERTY_NAME_REFERENCE[key]] = properties[key]

        return new_properties

    def update(self, dt):
        super().update(dt)
        for node in self.node_storage:
            node.on_update()

    def destroy(self):
        super().destroy()
        if self.root_node is not None: # Happens when scene is empty
            self.root_node.destroy()


class SceneManager(Manager):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.current_scene = None

    def instantiate_scene(self, scene):
        scene = Scene(self.game_manager, scene)
        if self.current_scene:
            self.current_scene.destroy()
        self.current_scene = scene

    def update(self, dt):
        super().update(dt)
        self.current_scene.update(dt)

    def destroy(self):
        super().destroy()
        self.current_scene.destroy()
