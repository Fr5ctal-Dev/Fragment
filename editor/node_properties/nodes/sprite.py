from .drawable import DrawableProperties
from ..property import Property


class SpriteProperties(DrawableProperties):
    @property
    def default_properties(self):
        properties = {
            'Sprite/Image Source': Property('Sprite/Image Source', 'path', '', 'Sprite', self),
        }
        return {**properties, **super().default_properties}
