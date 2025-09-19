from ..core.element import GameElement
from typing import Callable


class Node(GameElement):
    """The base class for all node objects.

    A node is defined as a class with a parent, children and properties.
    Every node has a node script, which is used to define custom logic using Python.
    Each node parents to other nodes to form a scene tree.
    """
    def __init__(self, game_manager, properties, uuid=None, parent=None, scene=None):
        super().__init__(game_manager)
        self.uuid = uuid
        self.name = None
        self.parent = None
        self.scene = scene
        self.children = []
        self.properties = properties
        self.set_parent(parent)

    def set_parent(self, node) -> None:
        if self.parent:
            self.parent.children.remove(self)
        self.parent = node
        if node:
            node.children.append(self)

    def initialize_properties(self, properties: dict) -> None:
        """Sets the properties in a dict onto the node."""
        for key in properties.keys():
            setattr(self, key, properties[key])

    def traverse(self, action: Callable) -> None:
        """Recursively performs an action on node and its children."""
        action(self)
        for child in self.children:
            child.traverse(action)

    def find_ancestor_of_type(self, node_type: type):
        """Finds nearest ancestor with a type satisfying node_type."""
        if self.parent is None:
            return

        current_node = self.parent
        while True:
            if isinstance(current_node, node_type):
                return current_node

            if current_node.parent is None:
                return
            current_node = current_node.parent

    def update(self, dt: float) -> None:
        self.on_update()

    def destroy(self) -> None:
        """Destroys node and children."""
        self.traverse(Node.destroy_self)

    def destroy_self(self) -> None:
        """Destroys node without destroying children."""
        self.on_destroy()
        if self.scene is not None:
            self.scene.unregister_node(self)

    def is_ancestor(self, node) -> bool:
        while True:
            if node == self:
                return True
            if not node.parent:
                return False
            node = node.parent

    @property
    def top_node(self):
        """Get the root node of the node tree the node is in."""
        current_node = self
        while True:
            if not current_node.parent:
                return current_node
            current_node = current_node.parent

    def on_start(self):
        pass

    def on_update(self):
        pass

    def on_destroy(self):
        pass
