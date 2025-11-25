from .manager import Manager
from ..types.vector import Vector2
from ..nodes.canvas import Canvas
from pygame_render import RenderEngine


class Renderer(Manager):
    """Renderer handles rendering in the application.

    Renderer overseas the rendering process of drawables onto the window.
    """
    def __init__(self, game_manager, window_manager, size: Vector2 = Vector2(1)):
        super().__init__(game_manager)
        self.window_manager = window_manager
        self.engine: RenderEngine = self.window_manager.window
        self.canvases = []
        self.engine.resize(int(size[0]), int(size[1]))


        self.placeholder_layer = self.engine.make_layer((1, 1))

    def setup_canvas(self):
        self.global_canvas = Canvas(self.game_manager, {}, is_global_canvas=True)

    def register_canvas(self, canvas: Canvas) -> None:
        self.canvases.append(canvas)

    @property
    def size(self) -> Vector2:
        return Vector2(self.surface.size)

    @size.setter
    def size(self, size: Vector2) -> None:
        self.surface = self.engine.make_layer((int(size[0]), int(size[1])))

    def update(self, dt: float) -> None:
        self.surface.clear(0, 0, 0, 0)
        self.engine.render(self.global_canvas.render().texture, self.surface, (0, 0))
        for canvas in self.canvases:
            self.engine.render(canvas.render().texture, self.surface, (0, 0))
