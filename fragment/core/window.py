from .manager import Manager
from .renderer import Renderer
from ..types.vector import Vector2
from pygame_render import RenderEngine
import pygame


class WindowManager(Manager):
    """The manager responsible for window management."""
    def __init__(self, game_manager, window_size: Vector2 = Vector2(0, 0), window_title: str = 'Made with Fragment'):
        super().__init__(game_manager)
        pygame.init()

        if window_size[0] == 0: window_size[0] = pygame.display.Info().current_w
        if window_size[1] == 0: window_size[1] = pygame.display.Info().current_h

        self.window = RenderEngine(int(window_size[0]), int(window_size[1]))

        self.renderer = Renderer(self.game_manager, self, window_size)

        self.window_size = window_size
        self.window_title = window_title

    @property
    def window_size(self) -> Vector2:
        return Vector2(pygame.display.get_window_size())

    @window_size.setter
    def window_size(self, size: Vector2):
        self.renderer.size = size # TODO: implement resizing of window

    @property
    def window_title(self) -> str:
        return pygame.display.get_caption()[0]

    @window_title.setter
    def window_title(self, title: str) -> None:
        pygame.display.set_caption(title)

    def update(self, dt: float) -> None:
        super().update(dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_manager.destroy()
        self.window.clear()
        self.renderer.update(dt)
        self.window.render(self.renderer.surface.texture, self.window.screen, (0, 0))
        pygame.display.flip()
