from .base_node import BaseNodeProperties
from ..property import NodeProperty


class NodeProperties(BaseNodeProperties):
    @property
    def default_properties(self):
        properties = {
            'Node/Name': NodeProperty(self, 'Node/Name', 'string', '', 'Node'),
            'Node/Script': NodeProperty(self, 'Node/Script', 'path_node_script', '', 'Node')
        }
        properties['Node/Name'].value_changed.connect(self.name_changed.emit)
        return {**properties, **super().default_properties}
