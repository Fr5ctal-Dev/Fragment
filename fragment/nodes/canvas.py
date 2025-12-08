from .node import Node
from ..types.vector import Vector2
from pygame_render import Layer


class Canvas(Node):
    """The node responsible for rendering drawables.

    Canvas will render all drawable descendants captured by its cameras.
    """
    def __init__(self, *args, is_global_canvas: bool = False, **kwargs):
        super().__init__(*args, **kwargs)
        self.drawables = {} # dict([drawable1, drawable2...])
        self.cameras = []

        self.render_layer = self.game_manager.window_manager.renderer.make_layer((int(self.size[0]), int(self.size[1])))

        if not is_global_canvas:
            self.game_manager.window_manager.register_canvas(self)

    @property
    def size(self) -> Vector2:
        return self.game_manager.window_manager.window_size

    def register_camera(self, camera) -> None:
        self.cameras.append(camera)

    def unregister_camera(self, camera) -> None:
        self.cameras.remove(camera)

    def register_drawable(self, drawable) -> None:
        if self.drawables.get(drawable.draw_priority) is None:
            self.drawables[drawable.draw_priority] = []
        self.drawables[drawable.draw_priority].append(drawable)

    def unregister_drawable(self, drawable) -> None:
        self.drawables[drawable.draw_priority].remove(drawable)
        if len(self.drawables[drawable.draw_priority]) == 0:
            self.drawables.pop(drawable.draw_priority)

    def sort_drawable_priorities(self) -> None:
        """Sorts drawables according to their draw priorities."""
        sorted_drawables = {}
        for priority in sorted(self.drawables):
            sorted_drawables[priority] = self.drawables[priority]
        self.drawables = sorted_drawables

    def render(self) -> Layer:
        """Renders drawables captured by its cameras."""
        self.sort_drawable_priorities()
        self.render_layer.clear(0, 0, 0, 0)
        for camera in self.cameras:
            layer = camera.render()
            self.game_manager.window_manager.renderer.render(layer.texture, self.render_layer, (0, 0), camera.zoom)

        return self.render_layer
    
    def update_size(self) -> None:
        """Updates the render layer size according to the window size."""
        self.render_layer = self.game_manager.window_manager.renderer.make_layer((int(self.size[0]), int(self.size[1])))
    
    @classmethod
    def view_mode(cls, *args, **kwargs):
        return Node(*args, **kwargs)
