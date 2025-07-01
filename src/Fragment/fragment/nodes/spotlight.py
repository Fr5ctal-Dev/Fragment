from .light import Light
from .node import Node
from rpcore import SpotLight as _SpotLight
from direct.showbase.Loader import Loader
from panda3d.core import CardMaker


class SpotLight(Light):
    def _get_node(self):
        self.light = _SpotLight()
        self.light.casts_shadows = True
        try:
            game.window.render_pipeline.add_light(self.light)
        except NameError:
            pass
        node = Node._get_node(self)
        return node

    def _update_light(self, task):
        try:
            self.light.direction = game.base_node._node.get_relative_vector(self._node, (0, 1, 0))
        except:
            try:
                self.light.direction = self._node.get_top().get_relative_vector(self._node, (0, 1, 0))
            except:
                pass
        return super()._update_light(task)

    @property
    def light_source_radius(self):
        return self._properties['light_source_radius']

    @light_source_radius.setter
    def light_source_radius(self, radius):
        self._properties['light_source_radius'] = radius
        self.light.fov = radius

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        node = cls(parent, path, **kwargs)
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
