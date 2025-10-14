from .node2d import Node2DProperties
from ..property import Property


class DrawableProperties(Node2DProperties):
    @property
    def default_properties(self):
        properties = {
            'Drawable/Draw Priority': Property('Drawable/Draw Priority', 'integer', 0, 'Drawable')
        }
        return {**properties, **super().default_properties}
