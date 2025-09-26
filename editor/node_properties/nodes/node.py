from .base_node import BaseNodeProperties
from ..property import Property


class NodeProperties(BaseNodeProperties):
    @property
    def default_properties(self):
        properties = {
            'name': Property('name', 'string', ''),
            'script': Property('script', 'path_node_script', '')
        }
        return {**properties, **super().default_properties}
