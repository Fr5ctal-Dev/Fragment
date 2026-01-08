from .drawable import DrawableProperties
from ..property import NodeProperty


class SpriteProperties(DrawableProperties):
    @property
    def default_properties(self):
        properties = {
            'Sprite/Image Source': NodeProperty(self, 'Sprite/Image Source', 'path', '', 'Sprite'),
        }
        return {**properties, **super().default_properties}
