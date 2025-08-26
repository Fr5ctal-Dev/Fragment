from .element import GameElement


class Manager(GameElement):
    """The base class for manager objects in the application"""
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.running = True

    def update(self, dt: float) -> None:
        """Update the manager.

        Args:
            dt (float): The delta time (dt) between the current and previous frame.
        """
        pass

    def destroy(self) -> None:
        """Destroy the manager."""
        self.running = False
