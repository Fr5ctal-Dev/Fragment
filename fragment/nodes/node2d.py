from .node import Node
from ..types.vector import Vector2


class Node2D(Node):
    """A node with a transform (position, rotation, scale etc.)."""
    @property
    def position(self) -> Vector2:
        return self.properties['position']

    @position.setter
    def position(self, position: Vector2) -> None:
        self.properties['position'] = Vector2(position)

    @property
    def world_position(self) -> Vector2:
        """The global position of node."""
        if (not self.parent) or (not hasattr(self.parent, 'world_position')):
            return self.position

        world_offset = self.position.rotate(self.parent.world_rotation)
        return self.parent.world_position + world_offset

    @property
    def rotation(self) -> float:
        return self.properties['rotation']

    @rotation.setter
    def rotation(self, rotation: float):
        self.properties['rotation'] = float(rotation)

    @property
    def world_rotation(self) -> float:
        """The global rotation of node."""
        if (not self.parent) or (not hasattr(self.parent, 'world_rotation')):
            return self.rotation

        return self.rotation + self.parent.world_rotation

    @property
    def scale(self) -> Vector2:
        return self.properties['scale']

    @scale.setter
    def scale(self, scale: Vector2) -> None:
        self.properties['scale'] = Vector2(scale)

    @property
    def world_scale(self) -> Vector2:
        """The global scale of node."""
        if (not self.parent) or (not hasattr(self.parent, 'world_scale')):
            return self.scale

        return Vector2(
            self.parent.world_scale.x * self.scale.x,
            self.parent.world_scale.y * self.scale.y
        )
