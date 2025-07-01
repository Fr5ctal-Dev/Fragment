from .node import Node
from .staticbody import StaticBody
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.core import BitMask32


class KinematicBody(Node):
    def full_init(self, shape):
        self.body = BulletCharacterControllerNode(shape, 0.4, 'body')
        nodepath = self._properties['parent']._node.attach_new_node(self.body)
        nodepath.set_collide_mask(BitMask32.all_on())
        self._node.reparent_to(nodepath)
        self._node.set_pos((0, 0, 0))
        self._node.set_scale((1, 1, 1))
        self._node.set_hpr((0, 0, 0))
        self._node = nodepath
        self._property_init()
        game.window.physics_world.attach_character(self.body)

    def destroy(self):
        game.window.physics_world.remove_character(self.body)
        super().destroy()

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return StaticBody(parent, path, **kwargs)

    @property
    def is_on_ground(self):
        return self._node.node().is_on_ground()

    @property
    def can_jump(self):
        return self._node.node().can_jump()

    def jump(self, max_jump_height=5.0, jump_speed=8.0):
        self._node.node().set_max_jump_height(max_jump_height)
        self._node.node().set_jump_speed(jump_speed)
        self._node.node().do_jump()
