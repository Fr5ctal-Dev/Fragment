from .node2d import Node2DProperties
from ..property import Property


class CameraProperties(Node2DProperties):
    @property
    def default_properties(self):
        properties = {
            'zoom': Property('zoom', 'float', 1.0)
        }
        return {**properties, **super().default_properties}
