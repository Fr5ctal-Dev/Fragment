from .node import NodeProperties
from ..property import NodeProperty


class Node2DProperties(NodeProperties):
    @property
    def default_properties(self):
        properties = {
            'Node2D/Position': NodeProperty(self, 'Node2D/Position', 'vector2', [0, 0], 'Node2D'),
            'Node2D/Rotation': NodeProperty(self, 'Node2D/Rotation', 'float', 0.0, 'Node2D'),
            'Node2D/Scale': NodeProperty(self, 'Node2D/Scale', 'vector2', [1, 1], 'Node2D')
        }
        return {**properties, **super().default_properties}
