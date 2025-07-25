from .manager import Manager
from .window import WindowManager
from .clock import Clock
from .scene_manager import SceneManager


class GameManager(Manager):
    def __init__(self, project_path):
        super().__init__(self)
        self.project_path = project_path
        self.window_manager = WindowManager(self)
        self.clock = Clock(self)
        self.scene_manager = SceneManager(self)

    def update(self, dt):
        super().update(dt)
        self.scene_manager.update(dt)
        self.clock.update(dt)
        self.window_manager.update(dt)

    def destroy(self):
        super().destroy()
        self.scene_manager.destroy()
        self.clock.destroy()
        self.window_manager.destroy()

    def run(self):
        while self.running:
            self.update(self.clock.dt)
