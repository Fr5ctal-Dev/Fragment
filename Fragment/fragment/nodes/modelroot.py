from .node import Node
from panda3d.core import NodePath


class ModelRoot(Node):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _get_node_from_model(self):
        curr_parent = self._properties['parent']
        while True:
            try:
                model = curr_parent.main_model
                break
            except:
                curr_parent = curr_parent.parent

        string_path = ''
        for name in self._properties['node_path'][1:]:
            string_path += name + '/'

        node = model.find(string_path[:-1])
        copied_node = NodePath(node.node().make_copy())
        copied_node.reparent_to(self._properties['parent']._node)
        return copied_node
