from .node import Node
from panda3d.bullet import BulletSphereShape


class SphereShape(Node):
    def _get_node(self):
        shape = BulletSphereShape(self._properties['radius'])
        try:
            self._properties['parent']._node.node().add_shape(shape)
        except:
            try:
                self._properties['parent'].full_init(shape)
            except BaseException as b:
                print(b)
        return super()._get_node()

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)
