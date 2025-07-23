from .manager import Manager
import time


class Clock(Manager):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.previous_time = time.time()
        self.current_time = time.time()

    def update_time(self):
        self.previous_time = self.current_time
        self.current_time = time.time()

    @property
    def dt(self):
        return self.current_time - self.previous_time

    @property
    def fps(self):
        return 1 / self.dt

    def update(self, dt):
        super().update(dt)
        self.update_time()
