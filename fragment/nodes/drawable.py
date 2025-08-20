from .node2d import Node2D
from .canvas import Canvas
import pygame


class Drawable(Node2D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = self.game_manager.window_manager.renderer
        self.target_canvas = self.find_ancestor_of_type(Canvas) or self.renderer.global_canvas
        self.target_canvas.register_drawable(self)

    def render(self):
        return pygame.Surface((1, 1), pygame.SRCALPHA) # Placeholder

    def destroy_self(self):
        self.target_canvas.unregister_drawable(self)
        super().destroy_self()
