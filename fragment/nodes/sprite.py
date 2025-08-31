from .drawable import Drawable
import pygame


class Sprite(Drawable):
    """Node that loads an image source to render on screen."""
    def __init__(self, *args, **kwargs):
        self.sprite_image = pygame.Surface((1, 1), pygame.SRCALPHA)
        super().__init__(*args, **kwargs)

    @property
    def image_source(self) -> str:
        return self.properties['image_source']

    @image_source.setter
    def image_source(self, source: str) -> None:
        self.properties['image_source'] = source
        self.sprite_image = pygame.image.load(self.properties['image_source']).convert_alpha()

    def image(self) -> pygame.Surface:
        return self.sprite_image
