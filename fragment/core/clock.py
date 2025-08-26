from .manager import Manager
import time


class Clock(Manager):
    """A clock object used for time related calculations and manipulations."""

    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.previous_time = time.time()
        self.current_time = time.time()

    def update_time(self) -> None:
        """Update the time of the clock using the time module."""
        self.previous_time = self.current_time
        self.current_time = time.time()

    @property
    def dt(self) -> float:
        """Delta time (dt) between the current and the previous frame.

        Delta time is the measure of the amount of time it took from
        the previous frame to the current frame.

        Returns:
            float: Delta time (dt) in seconds.
        """
        return self.current_time - self.previous_time

    @property
    def fps(self) -> float:
        """Frames per second (fps) between current and the previous frame.

        Frames per second (fps) is the number of frames that will pass in a second
        calculated by 1/delta time (dt).

        Returns:
            float: Frames per second (fps).
        """
        return 1 / self.dt

    def update(self, dt: float) -> None:
        super().update(dt)
        self.update_time()
