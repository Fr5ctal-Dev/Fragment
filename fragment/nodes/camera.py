from .node2d import Node2D
from .canvas import Canvas
from ..types.vector import Vector2
import pygame


class Camera(Node2D):
    """The node responsible for capturing and rendering the scene.

    The camera node detects the nearest canvas (if none found, it uses the global canvas)
    and renders onto that canvas. All the drawable descendants of that canvas will be
    rendered by the camera.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_canvas = self.find_ancestor_of_type(Canvas) or self.game_manager.window_manager.renderer.global_canvas
        self.target_canvas.register_camera(self)

    def render(self) -> pygame.Surface:
        """Render onto its target canvas."""
        drawables = self.target_canvas.drawables
        render_layer = pygame.Surface(self.view_size, pygame.SRCALPHA)
        render_rect = pygame.Rect((0, 0), self.view_size)
        for nodes in drawables.values():
            for node in nodes:
                draw_surface = node.render()
                rect = draw_surface.get_rect()
                rect.topleft = node.world_position - self.world_position # TODO: Adjust based on anchor and offset when it is added
                if render_rect.colliderect(rect): # Only render if on screen
                    render_layer.blit(draw_surface, rect)

        return render_layer

    @property
    def view_size(self) -> Vector2:
        """The view size of the camera, calculated by dividing its target canvas size with the zoom."""
        return self.target_canvas.size / self.zoom

    @property
    def zoom(self) -> float:
        return self.properties['zoom']

    @zoom.setter
    def zoom(self, zoom: float):
        self.properties['zoom'] = float(zoom)
