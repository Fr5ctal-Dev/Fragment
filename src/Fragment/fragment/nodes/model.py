from .node import Node
from panda3d.core import NodePath, StringStream, Loader


class Model(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _get_node(self):
        loader = Loader.get_global_ptr()

        ss_model = StringStream()
        with open(self._properties['model'], 'rb') as fp:
            ss_model.set_data(fp.read())

        self.main_model = NodePath(loader.load_bam_stream(ss_model))

        node = NodePath(self.main_model.node().make_copy())
        node.reparent_to(self._properties['parent']._node)
        return node
