from .manager import Manager
from ..nodes import NODES
from ..nodes.node import Node
import importlib
import json
from pathlib import Path

with open('fragment/nodes/name_ref.json') as f:
    content = json.loads(f.read())

PROPERTY_NAME_REFERENCE = {}
for value in list(content.values()):
    PROPERTY_NAME_REFERENCE = {**PROPERTY_NAME_REFERENCE, **value}


class Scene(Manager):
    """The manager responsible for scene and node instantiation, modification, management and deletion.

    The scene manager takes in a scene file and instantiates nodes accordingly.
    Scenes are often stored in the scene manager.
    """
    def __init__(self, game_manager, scene: str):
        super().__init__(game_manager)
        self.project_path = self.game_manager.project_path
        self.scene = scene
        self.root_node = None

        self.node_storage = [] # So you don't need to DFS the node tree every frame
        self.init()

    def init(self) -> None:
        """Fully initialize the scene.

        It creates, initializes and configures nodes based on its scene file.
        """
        with open(self.scene) as f:
            scene_content = f.read()
        scene_content = eval(scene_content)
        if not scene_content:
            return

        temp_node_storage = {}

        for node_path in list(scene_content.keys()):
            properties = {}
            for name, value in scene_content[node_path]['properties'].items():
                properties[name] = value['value'] # value of property

            if properties['script']:
                path = Path(properties['script']).relative_to(self.project_path)
                module = '.'.join(path.with_suffix('').parts)
                node_class = getattr(importlib.import_module(module), 'Node')
            else:
                node_class = NODES[scene_content[node_path]['type']]

            node = node_class(
                self.game_manager,
                self.convert_node_properties(properties),
                uuid=node_path[-1],
                parent=temp_node_storage[node_path[:-1]] if len(node_path) > 1 else None
            )

            node.initialize_properties(node.properties)

            if len(node_path) == 1:
                self.root_node = node

            temp_node_storage[node_path] = node
            self.register_node(node)

        for node in temp_node_storage.values():
            node.on_start()

    def register_node(self, node: Node) -> None:
        # TODO: Add unregister node
        self.node_storage.append(node)

    def convert_node_properties(self, properties: dict) -> dict:
        """Converts node property name from editor -> core

        Args:
            properties (dict): The properties of a node.

        Returns:
            dict: The modifies properties in terms of converting naming used in editor
            to the naming used in the core node classes. It uses nodes/name_ref.json as
            a reference.
        """
        new_properties = {}
        for key in list(properties.keys()):
            if PROPERTY_NAME_REFERENCE[key] is not None:
                new_properties[PROPERTY_NAME_REFERENCE[key]] = properties[key]

        return new_properties

    def update(self, dt: float) -> None:
        super().update(dt)
        for node in self.node_storage:
            node.on_update()

    def destroy(self) -> None:
        super().destroy()
        if self.root_node is not None: # Happens when scene is empty
            self.root_node.destroy()


class SceneManager(Manager):
    """The manager that manages scene objects."""
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.current_scene = None

    def instantiate_scene(self, scene_path: str) -> None:
        """Instantiates a scene based on scene file.

        Args:
            scene_path (str): The scene file path.
        """
        scene = Scene(self.game_manager, scene_path)
        if self.current_scene:
            self.current_scene.destroy()
        self.current_scene = scene

    def update(self, dt: float) -> None:
        super().update(dt)
        self.current_scene.update(dt)

    def destroy(self) -> None:
        super().destroy()
        self.current_scene.destroy()
