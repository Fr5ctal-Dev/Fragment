from panda3d.core import NodePath, CardMaker, CompassEffect
from ..vector import Vec3
import os
import builtins


class Node:
    def __init__(self, parent, path, **kwargs):
        self._properties = kwargs
        self._properties['parent'] = parent
        self._node = self._get_node()
        self._node_path = path
        self._property_init()
        self._node.set_python_tag('owner', self)
        try:
            self._update_task = taskMgr.add(self._update)
        except NameError:
            pass
        if not hasattr(builtins, 'game'):
            cm = CardMaker('card')
            cm.set_frame(-0.3, 0.3, -0.3, 0.3)
            card = cm.generate()
            card = self._node.attach_new_node(card)
            card.set_billboard_point_world()
            card.set_texture(loader.load_texture(kwargs['viewport_card_texture']))

            effect = CompassEffect.make(NodePath('compass'), CompassEffect.P_scale)
            card.set_effect(effect)
            card.set_bin('fixed', 100)
            card.set_depth_test(False)
            card.set_depth_write(False)

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        node = Node(parent, path, **kwargs)
        return node

    def _get_node(self):
        node = NodePath('node')
        if self._properties['parent']:
            node.reparent_to(self._properties['parent']._node)

        return node

    def destroy(self):
        self.on_destroy()
        taskMgr.remove(self._update_task)
        self._node.remove_node()

    def _property_init(self):
        for p in self._properties.keys():
            try:
                if p != 'parent':
                    exec(f'self.{p}')
                    exec(f'self.{p} = self._properties[p]')
            except AttributeError:
                pass

    def _update(self, task):
        self.on_update()
        return task.cont

    def point_at(self, position):
        self._node.look_at(position)
        self.rotation = self._node.get_hpr()

    def get_node(self, path):
        if path.startswith('/'):
            return game.get_node(path)
        else:
            amount = 0
            for ch in path:
                if ch == '.':
                    amount += 1
                else:
                    break
            path = path[amount:]
            self_node_path = self._node_path
            for i in range(amount + 1):
                self_node_path = os.path.dirname(self_node_path)
                if self_node_path == '/':
                    self_node_path = ''
                    break
            return game.get_node(self_node_path + '/' + path)

    def on_start(self):
        pass

    def on_update(self):
        pass

    def on_destroy(self):
        pass

    @property
    def parent(self):
        return self._properties['parent']

    @parent.setter
    def parent(self, parent):
        if not parent:
            return
        self._properties['parent'] = parent
        self._node.reparent_to(self._properties['parent']._node)

    @property
    def position(self):
        return Vec3(self._node.get_pos())

    @position.setter
    def position(self, position):
        self._properties['position'] = Vec3(position[0], position[1], position[2])
        self._node.set_pos(self._properties['position'])

    @property
    def rotation(self):
        return Vec3(self._node.get_hpr())

    @rotation.setter
    def rotation(self, rotation):
        self._properties['rotation'] = Vec3(rotation[0], rotation[1], rotation[2])
        self._node.set_hpr(self._properties['rotation'])

    @property
    def scale(self):
        return Vec3(self._node.get_scale())

    @scale.setter
    def scale(self, scale):
        if scale[0] == 0 or scale[1] == 0 or scale[2] == 0:
            return
        self._properties['scale'] = Vec3(scale[0], scale[1], scale[2])
        self._node.set_scale(self._properties['scale'])

    @property
    def forward(self):
        return self.parent._node.get_relative_vector(self._node, (0, 1, 0))

    @property
    def right(self):
        return self.parent._node.get_relative_vector(self._node, (1, 0, 0))

    @property
    def up(self):
        return self.parent._node.get_relative_vector(self._node, (0, 0, 1))

    @property
    def visible(self):
        return self._properties['visible']

    @visible.setter
    def visible(self, visible):
        self._properties['visible'] = visible
        if self._properties['visible']:
            self._node.show()
        else:
            self._node.hide()
