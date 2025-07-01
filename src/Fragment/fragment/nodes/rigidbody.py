from .staticbody import StaticBody
from panda3d.bullet import BulletRigidBodyNode


class RigidBody(StaticBody):
    def _get_node(self):
        self.body = BulletRigidBodyNode('Body')
        self.mass = self._properties['mass']
        node = self._properties['parent']._node.attach_new_node(self.body)
        game.window.physics_world.attach_rigid_body(self.body)
        return node

    @property
    def mass(self):
        return self.body.get_mass()

    @mass.setter
    def mass(self, mass):
        self._properties['mass'] = mass
        self.body.set_mass(mass)
