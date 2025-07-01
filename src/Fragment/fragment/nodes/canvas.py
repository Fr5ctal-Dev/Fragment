from .node import Node
from panda3d.core import NodePath


class Canvas(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        lens = base.cam2d.node().get_lens()
        lens.set_aspect_ratio(base.get_aspect_ratio())
        base.cam2d.node().set_lens(lens)
        self._node.reparent_to(NodePath())

    def _get_node(self):
        return render2d

    def destroy(self):
        pass
