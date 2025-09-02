from .node2d import Node2D
from .canvas import Canvas
from pygame_render import Texture


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

    def render(self) -> Texture:
        """Renders the drawable onto render layer."""
        texture = self.renderer.placeholder_layer.texture
        return texture

    def destroy_self(self) -> None:
        self.target_canvas.unregister_drawable(self)
        super().destroy_self()

    @property
    def draw_priority(self) -> int:
        return self.properties['draw_priority']

    @draw_priority.setter
    def draw_priority(self, priority: int) -> None:
        self.properties['draw_priority'] = int(priority)
