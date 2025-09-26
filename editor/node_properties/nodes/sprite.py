from .drawable import DrawableProperties
from ..property import Property


class SpriteProperties(DrawableProperties):
    @property
    def default_properties(self):
        properties = {
            'image_source': Property('image_source', 'path', '')
        }
        return {**properties, **super().default_properties}
