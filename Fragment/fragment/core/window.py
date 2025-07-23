from .manager import Manager
import pygame


class WindowManager(Manager):
    def __init__(self, game_manager, window_size = (0, 0), window_title = 'Made with Fragment'):
        super().__init__(game_manager)

        self.window_size = window_size
        self.window_title = window_title

        pygame.init()
        self.window = pygame.display.set_mode(self.window_size)

    @property
    def window_size(self):
        return pygame.display.get_window_size()

    @window_size.setter
    def window_size(self, size):
        self.window = pygame.display.set_mode(size)

    @property
    def window_title(self):
        return pygame.display.get_caption()[0]

    @window_title.setter
    def window_title(self, title):
        pygame.display.set_caption(title)

    def update(self, dt):
        super().update(dt)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_manager.destroy()
        pygame.display.update()
