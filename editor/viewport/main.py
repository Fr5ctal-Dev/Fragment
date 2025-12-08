from .renderer import WindowManager
from editor.qt_render import RenderEngine
from fragment.core.scene_manager import SceneManager
from fragment.types.vector import Vector2
from PySide6 import QtWidgets, QtCore


class Viewport(QtWidgets.QWidget):
    def __init__(self, project_path):
        super().__init__()
        self.project_path = project_path

        self.renderer = RenderEngine(800, 600)
        self.window_manager = None
        self.scene_manager = None

        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.addWidget(self.renderer)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(lambda: self.update_(0.016))

        self.check_gl_ctx_timer = QtCore.QTimer()
        self.check_gl_ctx_timer.timeout.connect(self.check_gl_ctx)
        self.check_gl_ctx_timer.start(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.window_manager is not None:
            self.window_manager.resize(Vector2(event.size().width(), event.size().height()))

    def check_gl_ctx(self):
        if self.renderer._ctx is not None:
            self.check_gl_ctx_timer.stop()
            self.full_init()

    def full_init(self):
        self.window_manager = WindowManager(self, renderer=self.renderer)
        self.window_manager.setup()
        self.window_manager.resize(Vector2(self.size().width(), self.size().height()))
        self.scene_manager = SceneManager(self, _view_mode=True)
        self.update_timer.start(16)

    def load_scene(self, scene_path):
        if self.scene_manager is None:
            return
        self.scene_manager.instantiate_scene(scene_path)

    def delete_node(self, uuid):
        pass

    def update_(self, dt):
        if self.scene_manager is None or self.window_manager is None:
            return
        self.scene_manager.update(dt)
        self.window_manager.update(dt)

    def destroy_(self):
        if self.scene_manager is None or self.window_manager is None:
            return
        self.scene_manager.destroy()
        self.window_manager.destroy()

