from .node2d import Node2D
from .canvas import Canvas
import pygame


class Drawable(Node2D):
    """The base node class for drawing things onto the screen.

    Drawable locates nearest Canvas ancestor (if none found, it uses the global canvas)
    and renders itself there.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.renderer = self.game_manager.window_manager.renderer
        self.target_canvas = self.find_ancestor_of_type(Canvas) or self.renderer.global_canvas
        self.target_canvas.register_drawable(self)

    def image(self) -> pygame.Surface:
        """The image of the drawable, without any post-processing done."""
        return pygame.Surface((1, 1), pygame.SRCALPHA) # Placeholder

    def render(self) -> pygame.Surface:
        """Renders the image of the drawable and applies post-processing."""
        image = self.image()
        return pygame.transform.rotate(pygame.transform.scale(image, (int(image.get_width() * self.world_scale[0]), int(image.get_height() * self.world_scale[1]))), -self.world_rotation)

    def destroy_self(self) -> None:
        self.target_canvas.unregister_drawable(self)
        super().destroy_self()

    @property
    def draw_priority(self) -> int:
        return self.properties['draw_priority']

    @draw_priority.setter
    def draw_priority(self, priority: int) -> None:
        self.properties['draw_priority'] = int(priority)
