from .node import Node
import pygame


class Canvas(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.drawables = [] # TODO: Keep them as a dict where the keys are their layers
        self.cameras = []

    def register_camera(self, camera):
        self.cameras.append(camera)

    def unregister_camera(self, camera):
        self.cameras.remove(camera)

    def register_drawable(self, drawable):
        self.drawables.append(drawable)

    def unregister_drawable(self, drawable):
        self.drawables.remove(drawable)

    def render(self):
        canvas_layer = pygame.Surface(self.game_manager.window_manager.renderer.size, pygame.SRCALPHA)
        for camera in self.cameras:
            surface = camera.render()
            canvas_layer.blit(surface, (0, 0))

        return canvas_layer
