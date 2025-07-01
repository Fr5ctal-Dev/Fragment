from .node import Node
from .staticbody import StaticBody
from panda3d.bullet import BulletGhostNode
from panda3d.core import BitMask32


class Ghost(Node):
    def _get_node(self):
        self.body = BulletGhostNode('Ghost')
        node = self._properties['parent']._node.attach_new_node(self.body)
        node.set_collide_mask(BitMask32(0x0f))
        try:
            game.window.physics_world.attach_ghost(self.body)
        except:
            node.get_top().get_python_tag('physics_world').attach_ghost(self.body)
        return node

    def _update(self, task):
        ghost = self._node.node()
        for node in ghost.get_overlapping_nodes():
            self.on_body_overlap(node.get_python_tag('owner'))
        return super()._update(task)

    def destroy(self):
        try:
            game.window.physics_world.remove_ghost(self.body)
        except:
            self._node.get_top().get_python_tag('physics_world').remove_ghost(self.body)
        super().destroy()

    def on_body_overlap(self, node):
        pass

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return StaticBody(parent, path, **kwargs)
