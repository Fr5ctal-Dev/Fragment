from .element import GameElement


class Manager(GameElement):
    def __init__(self, game_manager):
        super().__init__(game_manager)
        self.running = True

    def update(self, dt):
        pass

    def destroy(self):
        self.running = False
