from .node import Node
from panda3d.bullet import BulletBoxShape


class BoxShape(Node):
    def _get_node(self):
        shape = BulletBoxShape(tuple(self._properties['dimension']))
        try:
            self._properties['parent']._node.node().add_shape(shape)
        except:
            self._properties['parent'].full_init(shape)

        return super()._get_node()

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)
