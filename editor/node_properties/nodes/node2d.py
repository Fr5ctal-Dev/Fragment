from .node import NodeProperties
from ..property import Property


class Node2DProperties(NodeProperties):
    @property
    def default_properties(self):
        properties = {
            'Node2D/Position': Property('Node2D/Position', 'vector2', [0, 0], 'Node2D'),
            'Node2D/Rotation': Property('Node2D/Rotation', 'float', 0.0, 'Node2D'),
            'Node2D/Scale': Property('Node2D/Scale', 'vector2', [1, 1], 'Node2D')
        }
        return {**properties, **super().default_properties}
