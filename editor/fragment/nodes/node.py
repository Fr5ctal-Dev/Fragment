from ..core.element import GameElement


class Node(GameElement):
    def __init__(self, game_manager, properties):
        super().__init__(game_manager)
        self.name = None
        self.uuid = None
        self.parent = None
        self.children = []
        self.properties = properties
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
