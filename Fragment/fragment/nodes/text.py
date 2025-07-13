from .node import Node
from panda3d.core import TextNode
from ..vector import Vec4


class Text(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _get_node(self):
        text = TextNode('text')
        text.set_text('')
        node = self._properties['parent']._node.attach_new_node(text)
        return node

    @property
    def text(self):
        return self._properties['text']

    @text.setter
    def text(self, text):
        self._properties['text'] = str(text)
        self._node.node().set_text(self._properties['text'])

    @property
    def color(self):
        return self._properties['color']

    @color.setter
    def color(self, color):
        self._properties['color'] = Vec4(color[0], color[1], color[2], 1)
        self._node.set_color(self._properties['color'])
