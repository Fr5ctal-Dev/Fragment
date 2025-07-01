from .node import Node
from panda3d.core import PandaNode
from panda3d.core import CardMaker
from direct.showbase.Loader import Loader


class Camera(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_node(self):
        camera = PandaNode('camera')
        node = self._properties['parent']._node.attach_new_node(camera)
        game.window.camera.reparent_to(node)
        lens = game.window.cam.node().get_lens()
        lens.set_fov(self._properties['fov'])
        game.window.cam.node().set_lens(lens)
        return node

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        node = super().to_viewport(parent, path, **kwargs)
        cm = CardMaker('card')
        cm.set_frame(-0.3, 0.3, -0.3, 0.3)
        card = cm.generate()
        card = node._node.attach_new_node(card)
        card.set_two_sided(True)
        card.set_h(90)
        card.set_z(-0.4)

        card.set_bin('fixed', 100)
        card.set_depth_test(False)
        card.set_depth_write(False)

        loader = Loader(None)

        card.set_texture(loader.load_texture('assets/viewport_objects/arrow.png'))

        return node

    @property
    def fov(self):
        return self._properties['fov']

    @fov.setter
    def fov(self, fov):
        self._properties['fov'] = fov
        lens = game.window.cam.node().get_lens()
        lens.set_fov(fov)
        game.window.cam.node().set_lens(lens)
