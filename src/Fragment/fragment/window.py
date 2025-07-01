from rpcore import RenderPipeline
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFileData, WindowProperties
from panda3d.bullet import BulletWorld
import platform


class Window(ShowBase):
    def __init__(self, title='Made with Fragment'):
        loadPrcFileData('', f'window-title {title}')
        if platform.system() == 'Windows':
            loadPrcFileData('', 'icon-filename fragment/icon/icon_win.ico')
        else:
            loadPrcFileData('', 'icon-filename fragment/icon/icon.png')
        loadPrcFileData('', 'background-color 0.23 0.23 0.23 0.0')
        loadPrcFileData('', 'print-pipe-types false')

        self.render_pipeline = RenderPipeline()
        self.render_pipeline.pre_showbase_init()
        super().__init__()

        props = WindowProperties()
        props.set_size(self.pipe.get_display_width() - 10, self.pipe.get_display_height() - 100)
        self.win.request_properties(props)

        self.physics_world = BulletWorld()
        self.physics_world.set_gravity((0, 0, -9.81))

    def setup(self):
        self.render_pipeline.create(self)
        self.render_pipeline.daytime_mgr.time = 0.0

        self.taskMgr.add(self.update, 'update')
        self.disable_mouse()

    def update(self, task):
        dt = globalClock.get_dt()
        self.physics_world.do_physics(dt)
        return task.cont
