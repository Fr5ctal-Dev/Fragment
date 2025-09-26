from .node2d import Node2DProperties
from ..property import Property


class DrawableProperties(Node2DProperties):
    @property
    def default_properties(self):
        properties = {
            'draw_priority': Property('draw_priority', 'integer', 0)
        }
        return {**properties, **super().default_properties}
