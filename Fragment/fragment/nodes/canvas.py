from .node import Node
from panda3d.core import NodePath


class Canvas(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lens = self._window.cam2d.node().get_lens()
        lens.set_aspect_ratio(self._window.get_aspect_ratio())
        self._window.cam2d.node().set_lens(lens)
        self._node.reparent_to(NodePath())

    def _get_node(self):
        return render2d

    def destroy(self):
        pass
