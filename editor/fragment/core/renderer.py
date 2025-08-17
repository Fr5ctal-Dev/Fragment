from .manager import Manager
from ..types.vector import Vector2
import pygame


class Renderer(Manager):
    def __init__(self, game_manager, size = Vector2(0, 0)):
        super().__init__(game_manager)
        self.surface = pygame.Surface(size)

    @property
    def size(self):
        return Vector2(self.surface.get_size())

    @size.setter
    def size(self, size):
        self.surface = pygame.Surface(size)

    def update(self, dt):
        pass
