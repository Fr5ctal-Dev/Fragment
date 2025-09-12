from .node import NodeProperties


class CanvasProperties(NodeProperties):
    @property
    def default_properties(self):
        properties = {}
        return {**properties, **super().default_properties}
