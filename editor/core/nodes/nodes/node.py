from .base_node import BaseNodeProperties
from ..property import Property


class NodeProperties(BaseNodeProperties):
    @property
    def default_properties(self):
        properties = {
            'Node/Name': Property('Node/Name', 'string', '', 'Node', self),
            'Node/Script': Property('Node/Script', 'path_node_script', '', 'Node', self)
        }
        return {**properties, **super().default_properties}
