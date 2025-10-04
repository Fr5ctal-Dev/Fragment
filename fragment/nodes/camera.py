from .node2d import Node2D
from .canvas import Canvas
from ..types.vector import Vector2
from pygame_render import Layer


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
        self.render_layer = self.game_manager.window_manager.renderer.engine.make_layer((int(self.view_size[0]), int(self.view_size[1])))

    def render(self) -> Layer:
        """Render onto its target canvas."""
        self.render_layer.clear(0, 0, 0, 0)
        drawables = self.target_canvas.drawables
        for nodes in drawables.values():
            for node in nodes:
                draw_layer = node.render()
                if draw_layer is None:
                    continue
                position = node.world_position - self.world_position # TODO: Adjust based on anchor and offset when it is added
                self.game_manager.window_manager.renderer.engine.render(draw_layer, self.render_layer, position, angle=node.world_rotation, scale=node.world_scale)

        return self.render_layer

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
