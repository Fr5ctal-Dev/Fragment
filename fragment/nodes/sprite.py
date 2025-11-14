from .drawable import Drawable
from pygame_render import Texture


class Sprite(Drawable):
    """Node that loads an image source to render on screen."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sprite_image = None

    @property
    def image_source(self) -> str:
        return self.properties['image_source']

    @image_source.setter
    def image_source(self, source: str) -> None:
        self.properties['image_source'] = source
        self.sprite_image = self.window_manager.renderer.load_texture(self.properties['image_source'])

    def render(self) -> Texture:
        return self.sprite_image
