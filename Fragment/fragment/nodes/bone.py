from .modelroot import ModelRoot


class Bone(ModelRoot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.animation = None

    @classmethod
    def to_viewport(cls, parent, path, **kwargs):
        return cls(parent, path, **kwargs)

    def _get_node(self):
        curr_parent = self._properties['parent']
        while True:
            try:
                model = curr_parent.main_model
                break
            except:
                curr_parent = curr_parent.parent
        self.character_node = model
        return super()._get_node()

    @property
    def controlled(self):
        return self._properties['controlled']

    @controlled.setter
    def controlled(self, control):
        if control:
            self.character_node.control_joint(self._node, 'modelRoot', self._properties['bone_name'])
        else:
            self.character_node.release_joint('modelRoot', self._properties['bone_name'])
            self.character_node.expose_joint(self._node, 'modelRoot', self._properties['bone_name'])
