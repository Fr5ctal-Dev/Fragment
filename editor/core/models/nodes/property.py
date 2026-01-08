from editor.core.models.properties import Property


class NodeProperty(Property):
    def __init__(self, source_model, name, type, value, base_node_type, scene_override=False):
        super().__init__(source_model, name, type, value)
        self.base_node_type = base_node_type
        self.scene_override = scene_override

    def to_data(self):
        return {
            'name': self.name,
            'type': self.type,
            'value': self.value,
            'scene_override': self.scene_override
        }
