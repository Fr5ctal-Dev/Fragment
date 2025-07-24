# TODO: Finish this
from ..core.element import GameElement


class Node(GameElement):
    def __init__(self, game_manager, properties):
        super().__init__(game_manager)
        self.name = None
        self.uuid = None
        self.parent = None
        self.children = []
        self.properties = properties # TODO: Implement the properties and property initialization

    def set_parent(self, node):
        if self.parent:
            self.parent.children.remove(self)
        self.parent = node
        if node:
            node.children.apend(self)

    def update(self, dt):
        self.on_update()

    def destroy(self):
        self.on_destroy()

    def on_start(self):
        pass

    def on_update(self):
        pass

    def on_destroy(self):
        pass
