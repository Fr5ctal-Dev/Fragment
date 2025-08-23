from .node2d import Node2D
from .canvas import Canvas
import pygame


class Camera(Node2D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_canvas = self.find_ancestor_of_type(Canvas) or self.game_manager.window_manager.renderer.global_canvas
        self.target_canvas.register_camera(self)

    def render(self):
        drawables = self.target_canvas.drawables
        render_layer = pygame.Surface(self.target_canvas.size, pygame.SRCALPHA)
        render_rect = pygame.Rect((0, 0), self.target_canvas.size / self.zoom)
        for nodes in drawables.values():
            for node in nodes:
                draw_surface = node.render()
                rect = draw_surface.get_rect()
                rect.topleft = node.world_position - self.world_position # TODO: Adjust based on anchor and offset when it is added
                if render_rect.colliderect(rect): # Only render if on screen
                    render_layer.blit(draw_surface, rect)

        return render_layer

    @property
    def view_size(self):
        return self.game_manager.window_manager.renderer.size / self.zoom

    @property
    def zoom(self):
        return self.properties['zoom']

    @zoom.setter
    def zoom(self, zoom):
        self.properties['zoom'] = float(zoom)
