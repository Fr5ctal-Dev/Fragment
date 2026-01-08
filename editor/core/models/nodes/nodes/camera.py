from .node2d import Node2DProperties
from ..property import NodeProperty


class CameraProperties(Node2DProperties):
    @property
    def default_properties(self):
        properties = {
            'Camera/Zoom': NodeProperty(self, 'Camera/Zoom', 'float', 1.0, 'Camera')
        }
        return {**properties, **super().default_properties}
