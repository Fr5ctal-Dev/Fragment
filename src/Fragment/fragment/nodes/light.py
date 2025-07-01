from .node import Node
from rpcore import PointLight
from ..vector import Vec3


class Light(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.light_update_task = taskMgr.add(self._update_light, 'update_light')

    def _get_node(self):
        self.light = PointLight()
        self.light.casts_shadows = True
        try:
            game.window.render_pipeline.add_light(self.light)
        except NameError:
            pass
        node = super()._get_node()
        return node

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _update_light(self, task):
        try:
            self.light.pos = self._node.get_pos(game.base_node._node)
        except:
            self.light.pos = self._node.get_pos(self._node.get_top())
        return task.cont

    def destroy(self):
        taskMgr.remove(self.light_update_task)
        try:
            game.window.render_pipeline.remove_light(self.light)
        except:
            self._node.get_top().get_python_tag('render_pipeline').remove_light(self.light)
        super().destroy()

    @property
    def color(self):
        return self._properties['color']

    @color.setter
    def color(self, color):
        self._properties['color'] = Vec3(color[0], color[1], color[2])
        self.light.color = self._properties['color']

    @property
    def strength(self):
        return self._properties['strength']

    @strength.setter
    def strength(self, strength):
        self._properties['strength'] = strength
        self.light.energy = strength * 1000

    @property
    def light_source_radius(self):
        return self._properties['light_source_radius']

    @light_source_radius.setter
    def light_source_radius(self, radius):
        self._properties['light_source_radius'] = radius
        self.light.inner_radius = radius

    @property
    def light_travel_radius(self):
        return self._properties['light_travel_radius']

    @light_travel_radius.setter
    def light_travel_radius(self, radius):
        self._properties['light_travel_radius'] = radius
        self.light.radius = radius
