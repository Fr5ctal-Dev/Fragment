from fragment.core.manager import Manager
from fragment.types.vector import Vector2
from fragment.nodes.canvas import Canvas
from fragment.nodes.camera import Camera
from editor.qt_render import RenderEngine


class WindowManager(Manager):
    """The manager responsible for window management."""
    def __init__(self, game_manager, renderer: RenderEngine, window_size: Vector2 = Vector2(800, 600), window_title: str = 'Made with Fragment'):
        super().__init__(game_manager)
        self.renderer = renderer

        self.window_size = window_size
        self.window_title = window_title

        self.canvases = []
        self.surface = self.renderer.make_layer((int(self.window_size[0]), int(self.window_size[1])))

        self.placeholder_layer = self.renderer.make_layer((1, 1))

    def resize(self, size: Vector2):
        self.window_size = Vector2(size)
        self.surface.release()
        self.surface = self.renderer.make_layer((int(size[0]), int(size[1])))
        self.renderer.resize(int(size[0]), int(size[1]))

        self.global_canvas.update_size()
        self.global_camera.update_size()

    def setup(self):
        self.global_canvas = Canvas(self.game_manager, {}, is_global_canvas=True)
        self.global_camera = Camera(self.game_manager, {
            'position': (0.0, 0.0),
            'zoom': 1.0
        })

    def register_canvas(self, canvas: Canvas) -> None:
        self.canvases.append(canvas)

    def update(self, dt: float) -> None:
        super().update(dt)
        self.renderer.makeCurrent()

        self.renderer.clear()
        self.surface.clear()

        self.renderer.render(self.global_canvas.render().texture, self.surface, (0, 0))

        for canvas in self.canvases:
            self.renderer.render(canvas.render().texture, self.surface, (0, 0))

        self.renderer.render(self.surface.texture, self.renderer.screen, (0, 0))

        self.renderer.update()
