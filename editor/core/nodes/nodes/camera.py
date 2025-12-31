from .node2d import Node2DProperties
from ..property import Property


class CameraProperties(Node2DProperties):
    @property
    def default_properties(self):
        properties = {
            'Camera/Zoom': Property('Camera/Zoom', 'float', 1.0, 'Camera', self)
        }
        return {**properties, **super().default_properties}
