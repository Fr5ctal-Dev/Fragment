from moderngl import Texture, Framebuffer
from editor.qt_render.util import normalize_color_arguments


class Layer:

    def __init__(self, tex: Texture, fbo: Framebuffer, logical_size: tuple[int, int] = None) -> None:

        self._tex = tex
        self._fbo = fbo
        self._logical_size = logical_size

    @property
    def texture(self) -> Texture:
        return self._tex

    @property
    def framebuffer(self) -> Framebuffer:
        return self._fbo

    @property
    def size(self) -> tuple[int, int]:
        return self._logical_size if self._logical_size else self._fbo.size

    @property
    def width(self) -> int:
        return self._logical_size[0] if self._logical_size else self._fbo.width

    @property
    def height(self) -> int:
        return self._logical_size[1] if self._logical_size else self._fbo.height

    def clear(self, R: (int | tuple[int]) = 0, G: int = 0, B: int = 0, A: int = 255):
        R, G, B, A = normalize_color_arguments(R, G, B, A)
        self._fbo.clear(R, G, B, A)

    def release(self):
        if self._tex is not None:
            self._tex.release()
        self._fbo.release()
