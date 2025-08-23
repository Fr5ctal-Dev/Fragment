from .node import Node
import pygame


class Canvas(Node):
    def __init__(self, *args, is_global_canvas=False, **kwargs):
        super().__init__(*args, **kwargs)
        self.drawables = {} # dict([drawable1, drawable2...])
        self.cameras = []
        if not is_global_canvas:
            self.game_manager.window_manager.renderer.register_canvas(self)

    @property
    def size(self):
        return self.game_manager.window_manager.renderer.size

    def register_camera(self, camera):
        self.cameras.append(camera)

    def unregister_camera(self, camera):
        self.cameras.remove(camera)

    def register_drawable(self, drawable):
        if self.drawables.get(drawable.draw_priority) is None:
            self.drawables[drawable.draw_priority] = []
        self.drawables[drawable.draw_priority].append(drawable)

    def unregister_drawable(self, drawable):
        self.drawables[drawable.draw_priority].remove(drawable)
        if len(self.drawables[drawable.draw_priority]) == 0:
            self.drawables.pop(drawable.draw_priority)

    def sort_drawable_priorities(self):
        sorted_drawables = {}
        for priority in sorted(self.drawables):
            sorted_drawables[priority] = self.drawables[priority]
        self.drawables = sorted_drawables

    def render(self):
        self.sort_drawable_priorities()
        canvas_layer = pygame.Surface(self.size, pygame.SRCALPHA)
        for camera in self.cameras:
            surface = camera.render()
            canvas_layer.blit(pygame.transform.scale(surface, self.size), (0, 0))

        return canvas_layer
