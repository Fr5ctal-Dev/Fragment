from .manager import Manager
from ..types.vector import Vector2
from ..nodes.canvas import Canvas
import pygame


class Renderer(Manager):
    def __init__(self, game_manager, size = Vector2(0, 0)):
        super().__init__(game_manager)
        self.surface = pygame.Surface(size)
        self.canvases = []
        self.global_canvas = Canvas(self.game_manager, {}, is_global_canvas=True)

    def register_canvas(self, canvas):
        self.canvases.append(canvas)

    @property
    def size(self):
        return Vector2(self.surface.get_size())

    @size.setter
    def size(self, size):
        self.surface = pygame.Surface(size)

    def update(self, dt):
        self.surface.blit(self.global_canvas.render(), (0, 0))
        for canvas in self.canvases:
            self.surface.blit(canvas.render(), (0, 0))
