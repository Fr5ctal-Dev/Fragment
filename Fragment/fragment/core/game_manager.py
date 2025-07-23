from .manager import Manager
from .window import WindowManager
from .clock import Clock


class GameManager(Manager):
    def __init__(self):
        super().__init__(self)
        self.window_manager = WindowManager(self)
        self.clock = Clock(self)

    def update(self, dt):
        super().update(dt)
        self.window_manager.update(dt)
        self.clock.update(dt)

    def destroy(self):
        super().destroy()
        self.window_manager.destroy()
        self.clock.destroy()

    def run(self):
        while self.running:
            self.update(self.clock.dt)
