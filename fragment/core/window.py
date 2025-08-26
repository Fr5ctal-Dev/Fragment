from .manager import Manager
from .renderer import Renderer
from ..types.vector import Vector2
import pygame


class WindowManager(Manager):
    """The manager responsible for window management."""
    def __init__(self, game_manager, window_size: Vector2 = Vector2(0, 0), window_title: str = 'Made with Fragment'):
        super().__init__(game_manager)
        pygame.init()

        if window_size[0] == 0: window_size[0] = pygame.display.Info().current_w
        if window_size[1] == 0: window_size[1] = pygame.display.Info().current_h

        self.renderer = Renderer(self.game_manager)

        self.window_size = window_size
        self.window_title = window_title

        self.window = pygame.display.set_mode(self.window_size)

    @property
    def window_size(self) -> Vector2:
        return Vector2(pygame.display.get_window_size())

    @window_size.setter
    def window_size(self, size: Vector2):
        self.renderer.size = size
        self.window = pygame.display.set_mode(size)

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
        self.window.fill((0, 0, 0))
        self.renderer.update(dt)
        self.window.blit(self.renderer.surface, (0, 0))
        pygame.display.update()
