from .modelroot import ModelRoot


class AnimationBundle(ModelRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _get_node(self):
        return self._get_node_from_model()
