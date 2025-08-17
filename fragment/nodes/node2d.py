from .node import Node
from ..types.vector import Vector2


class Node2D(Node):
    @property
    def position(self):
        return self.properties['position']

    @position.setter
    def position(self, position):
        self.properties['position'] = Vector2(position[0], position[1])

    @property
    def world_position(self):
        if (not self.parent) or (not hasattr(self.parent, 'world_position')):
            return self.position

        world_offset = self.position.rotate(self.parent.world_rotation)
        return self.parent.world_position + world_offset

    @property
    def rotation(self):
        return self.properties['rotation']

    @rotation.setter
    def rotation(self, rotation):
        self.properties['rotation'] = float(rotation)

    @property
    def world_rotation(self):
        if (not self.parent) or (not hasattr(self.parent, 'world_rotation')):
            return self.rotation

        return self.rotation + self.parent.world_rotation

    @property
    def scale(self):
        return self.properties['scale']

    @scale.setter
    def scale(self, scale):
        self.properties['scale'] = Vector2(scale[0], scale[1])

    @property
    def world_scale(self):
        if (not self.parent) or (not hasattr(self.parent, 'world_scale')):
            return self.scale

        return Vector2(
            self.parent.world_scale.x * self.scale.x,
            self.parent.world_scale.y * self.scale.y
        )
