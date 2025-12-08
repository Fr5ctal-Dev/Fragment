from importlib import resources
import enum


try:
    import numpy as np
except ImportError:
    raise ImportError('Missing package: numpy.')
except Exception as e:
    raise ImportError(f'Error importing numpy: {e}')

try:
    from PySide6 import QtCore, QtGui, QtWidgets, QtOpenGLWidgets
except ImportError:
    raise ImportError('Missing package: PySide6.')
except Exception as e:
    raise ImportError(f'Error importing PySide6: {e}')

try:
    import moderngl
except ImportError:
    raise ImportError('Missing package: moderngl.')
except Exception as e:
    raise ImportError(f'Error importing moderngl: {e}')


from .engine import RenderEngine, Rect
from .layer import Layer
from .shader import Shader
from .font_atlas import FontAtlas
from moderngl import Program, Buffer, Framebuffer, Texture

NEAREST = moderngl.NEAREST
LINEAR = moderngl.LINEAR

__all__ = ['RenderEngine', 'FontAtlas', 'Layer', 'Shader', 'Program', 'Buffer',
           'Framebuffer', 'Texture', 'NEAREST', 'LINEAR', 'Rect']

__version__ = '1.4.2'
