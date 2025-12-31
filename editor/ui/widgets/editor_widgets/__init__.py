from .string import String
from .float import Float
from .integer import Integer
from .vector2 import Vector2
from .path import Path
from .path_script import PathScript
from .path_node_script import PathNodeScript

EDITOR_WIDGETS = {
    'string': String,
    'float': Float,
    'integer': Integer,
    'vector2': Vector2,
    'path': Path,
    'path_script': PathScript,
    'path_node_script': PathNodeScript,
}
