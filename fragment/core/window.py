from .manager import Manager
from ..types.vector import Vector2
from ..nodes.canvas import Canvas
from pygame_render import RenderEngine
import pygame


class WindowManager(Manager):
    """The manager responsible for window management."""
    def __init__(self, game_manager, window_size: Vector2 = Vector2(0, 0), window_title: str = 'Made with Fragment'):
        super().__init__(game_manager)
        pygame.init()

        if window_size[0] == 0:
            window_size[0] = pygame.display.Info().current_w
        if window_size[1] == 0:
            window_size[1] = pygame.display.Info().current_h

        self.renderer = RenderEngine(int(window_size[0]), int(window_size[1]))

        self.window_size = window_size
        self.window_title = window_title

        self.canvases = []
        self.surface = self.renderer.make_layer((int(self.window_size[0]), int(self.window_size[1])))

        self.placeholder_layer = self.renderer.make_layer((1, 1))

    @property
    def window_size(self) -> Vector2:
        return Vector2(pygame.display.get_window_size())

    @window_size.setter
    def window_size(self, size: Vector2):
        self.surface = self.renderer.make_layer((int(size[0]), int(size[1])))

    @property
    def window_title(self) -> str:
        return pygame.display.get_caption()[0]

    @window_title.setter
    def window_title(self, title: str) -> None:
        pygame.display.set_caption(title)

    def setup_canvas(self):
        self.global_canvas = Canvas(self.game_manager, {}, is_global_canvas=True)

    def register_canvas(self, canvas: Canvas) -> None:
        self.canvases.append(canvas)

    def update(self, dt: float) -> None:
        super().update(dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_manager.destroy()

        self.renderer.clear()
        self.surface.clear()

        self.renderer.render(self.global_canvas.render().texture, self.surface, (0, 0))

        for canvas in self.canvases:
            self.renderer.render(canvas.render().texture, self.surface, (0, 0))

        self.renderer.render(self.surface.texture, self.renderer.screen, (0, 0))

        pygame.display.flip()
