from .manager import Manager
from .window import WindowManager
from .clock import Clock
from .scene_manager import SceneManager


class GameManager(Manager):
    """The central manager responsible for coordinating the application.

    The GameManager serves as the top-level manager, supervising all
    other managers within the application. It is responsible for overseeing
    core components such as task scheduling, window management, scene handling,
    and other high-level systems.
    """
    def __init__(self, project_path: str):
        super().__init__(self)
        self.project_path = project_path
        self.window_manager = WindowManager(self)
        self.window_manager.renderer.setup_canvas()
        self.clock = Clock(self)
        self.scene_manager = SceneManager(self)

    def update(self, dt: float) -> None:
        super().update(dt)
        self.scene_manager.update(dt)
        self.clock.update(dt)
        self.window_manager.update(dt)

    def destroy(self) -> None:
        super().destroy()
        self.scene_manager.destroy()
        self.clock.destroy()
        self.window_manager.destroy()

    def run(self) -> None:
        """Run the application with a main loop."""
        while self.running:
            self.update(self.clock.dt)
