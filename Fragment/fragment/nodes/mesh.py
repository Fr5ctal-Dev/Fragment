from .modelroot import ModelRoot


class Mesh(ModelRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _get_node(self):
        node = self._get_node_from_model()
        node.set_python_tag('viewport_pickable', self)
        return node
