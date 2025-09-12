from .nodes.node import NodeProperties
from .nodes.node2d import Node2DProperties
from .nodes.canvas import CanvasProperties
from .nodes.drawable import DrawableProperties
from .nodes.camera import CameraProperties
from .nodes.sprite import SpriteProperties

node_properties = {
    'Node': NodeProperties,
    'Node2D': Node2DProperties,
    'Canvas': CanvasProperties,
    'Drawable': DrawableProperties,
    'Camera': CameraProperties,
    'Sprite': SpriteProperties
}
