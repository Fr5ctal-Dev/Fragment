from .node import Node
from panda3d.bullet import BulletRigidBodyNode


class StaticBody(Node):
    def _get_node(self):
        self.body = BulletRigidBodyNode('Body')
        node = self._properties['parent']._node.attach_new_node(self.body)
        try:
            game.window.physics_world.attach_rigid_body(self.body)
        except:
            node.get_top().get_python_tag('physics_world').attach_rigid_body(self.body)
        return node

    def destroy(self):
        try:
            game.window.physics_world.remove_rigid_body(self.body)
        except:
            self._node.get_top().get_python_tag('physics_world').remove_rigid_body(self.body)
        super().destroy()

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    @property
    def friction(self):
        return self._properties['friction']

    @friction.setter
    def friction(self, friction):
        self._properties['friction'] = friction
        self.body.set_friction(friction)

    @property
    def elasticity(self):
        return self._properties['friction']

    @elasticity.setter
    def elasticity(self, elasticity):
        self._properties['elasticity'] = elasticity
        self.body.set_restitution(elasticity)
