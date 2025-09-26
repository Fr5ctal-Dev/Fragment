from .node import NodeProperties
from ..property import Property


class Node2DProperties(NodeProperties):
    @property
    def default_properties(self):
        properties = {
            'position': Property('position', 'vector2', [0, 0]),
            'rotation': Property('rotation', 'float', 0.0),
            'scale': Property('scale', 'vector2', [1, 1])
        }
        return {**properties, **super().default_properties}
