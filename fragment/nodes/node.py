from ..core.element import GameElement


class Node(GameElement):
    def __init__(self, game_manager, properties, name=None, uuid=None, parent=None):
        super().__init__(game_manager)
        self.name = name
        self.uuid = uuid
        self.parent = None
        self.children = []
        self.properties = properties
        self.set_parent(parent)
        self.initialize_properties(self.properties)

    def set_parent(self, node):
        if self.parent:
            self.parent.children.remove(self)
        self.parent = node
        if node:
            node.children.append(self)

    def initialize_properties(self, properties):
        for key in properties.keys():
            setattr(self, key, properties[key])

    def traverse(self, action):
        action(self)
        for child in self.children:
            child.traverse(action)

    def find_ancestor_of_type(self, node_type):
        if self.parent is None:
            return

        current_node = self.parent
        while True:
            if isinstance(current_node, node_type):
                return current_node

            if current_node.parent is None:
                return
            current_node = current_node.parent

    def update(self, dt):
        self.on_update()

    def destroy(self):
        self.traverse(Node.destroy_self)

    def destroy_self(self): # Destroys node without destroying children
        self.on_destroy()

    def is_ancestor(self, node):
        while True:
            if node == self:
                return True
            if not node.parent:
                return False
            node = node.parent

    @property
    def top_node(self):
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
