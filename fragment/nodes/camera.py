from .node2d import Node2D
from .canvas import Canvas
import pygame


class Camera(Node2D):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_canvas = self.find_ancestor_of_type(Canvas) or self.game_manager.window_manager.renderer.global_canvas
        self.target_canvas.register_camera(self)

    def render(self):
        pass # TODO

    @property
    def view_size(self):
        return self.game_manager.window_manager.renderer.size / self.zoom

    @property
    def zoom(self):
        return self.properties['zoom']

    @zoom.setter
    def zoom(self, zoom):
        self.properties['zoom'] = float(zoom)
