from importlib import resources
import warnings
import numbers
from math import sin, cos

import moderngl
from moderngl import Texture, Context, NEAREST
import numpy as np
from OpenGL.GL import glGetUniformBlockIndex, glUniformBlockBinding
from PySide6.QtOpenGLWidgets import QOpenGLWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage

from editor.qt_render.font_atlas import FontAtlas
from editor.qt_render.layer import Layer
from editor.qt_render.shader import Shader
from editor.qt_render.util import (
    normalize_color_arguments,
    create_rotated_rect,
    to_dest_coords,
    to_source_coords,
)


class Rect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height


class RenderEngine(QOpenGLWidget):

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        parent=None
    ) -> None:
        super().__init__(parent)

        self._screen_width = screen_width
        self._screen_height = screen_height
        self.resize(screen_width, screen_height)

        self._ctx = None
        self._screen = None
        self._shader_draw = None
        self._shader_tonemap = None
        self._shader_text = None
        self.prog_prim = None
        self._exposure = 0.1

    def initializeGL(self):
        self._ctx = moderngl.create_context()

        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE_MINUS_SRC_ALPHA,
        )
        self._ctx.blend_equation = moderngl.FUNC_ADD

        default_fbo = self._ctx.detect_framebuffer(self.defaultFramebufferObject())
        self._screen = Layer(None, default_fbo, logical_size=(self._screen_width, self._screen_height))

        self._ctx.viewport = (0, 0, *default_fbo.size)

        vertex_src = resources.read_text('editor.qt_render', 'vertex.glsl')
        fragment_src_draw = resources.read_text('editor.qt_render', 'fragment_draw.glsl')

        prog_draw = self._ctx.program(
            vertex_shader=vertex_src, fragment_shader=fragment_src_draw
        )
        self._shader_draw = Shader(prog_draw)

        fragment_src_tonemap = resources.read_text(
            'editor.qt_render', 'fragment_tone.glsl'
        )

        prog_tonemap = self._ctx.program(
            vertex_shader=vertex_src, fragment_shader=fragment_src_tonemap
        )
        self._shader_tonemap = Shader(prog_tonemap)
        self.HDR_exposure = 0.1

        self.prog_prim = self.ctx.program(
            vertex_shader='''
            #version 330
            in vec2 vert;
            void main() {
            gl_Position = vec4(vert.x, vert.y, 0.0, 1.0);
            }''',
            fragment_shader='''
            #version 330
            uniform vec4 primColor;
            out vec4 color;
            void main() {
            color = primColor;
            }''',
        )

        fragment_src_text = resources.read_text('editor.qt_render', 'fragment_text.glsl')

        prog_text = self._ctx.program(
            vertex_shader=vertex_src, fragment_shader=fragment_src_text
        )
        self._shader_text = Shader(prog_text)

    @property
    def screen(self) -> Layer:
        return self._screen

    @property
    def ctx(self) -> Context:
        return self._ctx

    def paintGL(self):
        pass

    def resizeGL(self, w, h):
        if self._ctx:
            self._screen_width = w
            self._screen_height = h

            default_fbo = self._ctx.detect_framebuffer(self.defaultFramebufferObject())
            self._screen = Layer(None, default_fbo, logical_size=(w, h))

            self._ctx.viewport = (0, 0, *default_fbo.size)

    @property
    def display_size(self) -> tuple[int, int]:
        return (self._screen_width, self._screen_height)

    @property
    def HDR_exposure(self) -> float:
        return self._exposure

    @HDR_exposure.setter
    def HDR_exposure(self, value: float) -> None:
        self._exposure = value
        self._shader_tonemap['exposure'] = value

    def use_alpha_blending(self, enabled: bool) -> None:
        if enabled:
            self._ctx.enable(moderngl.BLEND)
        else:
            self._ctx.disable(moderngl.BLEND)

    def use_premultiplied_alpha_mode(self) -> None:
        self._ctx.blend_func = (moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)

    def use_standard_alpha_mode(self) -> None:
        self._ctx.blend_func = (moderngl.SRC_ALPHA, moderngl.ONE_MINUS_SRC_ALPHA,
                                moderngl.ONE, moderngl.ONE_MINUS_SRC_ALPHA)

    def qimage_to_texture(self, img: QImage) -> moderngl.Texture:
        img = img.convertToFormat(QImage.Format_RGBA8888)

        img = img.mirrored(False, True)

        ptr = img.constBits()
        img_data = ptr.tobytes()

        tex = self._ctx.texture((img.width(), img.height()), components=4, data=img_data)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        return tex

    def load_texture(self, path: str) -> moderngl.Texture:
        img = QImage(path)
        if img.isNull():
            raise ValueError(f'Failed to load image from {path}')
        return self.qimage_to_texture(img)

    def make_layer(
        self,
        size: tuple[int, int],
        components: int = 4,
        data: bytes | None = None,
        samples: int = 0,
        alignment: int = 1,
        dtype: str = 'f1',
        internal_format: int | None = None,
    ) -> Layer:
        tex = self.ctx.texture(
            size,
            components,
            data,
            samples=samples,
            alignment=alignment,
            dtype=dtype,
            internal_format=internal_format,
        )
        tex.filter = (NEAREST, NEAREST)
        fbo = self.ctx.framebuffer([tex])
        return Layer(tex, fbo)

    def make_shader(self, vertex_src: str, fragment_src: str) -> Shader:
        prog = self.ctx.program(vertex_shader=vertex_src, fragment_shader=fragment_src)
        shader = Shader(prog)
        return shader

    def make_font_atlas(self, font_path: str = None, font_size: int = 64) -> FontAtlas:
        return FontAtlas(self, font_path, font_size)

    def load_shader_from_path(self, vertex_path: str, fragment_path: str) -> Shader:
        with open(vertex_path) as f:
            vertex_src = f.read()
        with open(fragment_path) as f:
            fragment_src = f.read()

        return self.make_shader(vertex_src, fragment_src)

    def reserve_uniform_block(self, shader: Shader, ubo_name: str, nbytes: int) -> None:
        prog_glo = shader.program.glo

        binding = shader.sample_ubo_binding()
        block_index = glGetUniformBlockIndex(prog_glo, ubo_name)
        glUniformBlockBinding(prog_glo, block_index, binding)

        ubo = self.ctx.buffer(reserve=nbytes)
        ubo.bind_to_uniform_block(binding)
        shader.add_ubo(ubo, ubo_name)

    def clear(self, R: int | tuple[int] = 0, G: int = 0, B: int = 0, A: int = 255):
        R, G, B, A = normalize_color_arguments(R, G, B, A)
        self._screen.framebuffer.clear(R, G, B, A)

    def render(
        self,
        tex: Texture,
        layer: Layer,
        position: tuple[float, float] = (0, 0),
        scale: tuple[float, float] | float = (1.0, 1.0),
        angle: float = 0.0,
        flip: tuple[bool, bool] | bool = (False, False),
        section: Rect | None = None,
        shader: Shader = None,
        hdr_render: bool = False,
    ) -> None:

        if section is None:
            section = Rect(0, 0, tex.width, tex.height)

        if isinstance(scale, numbers.Number):
            scale = (scale, scale)

        if isinstance(flip, bool):
            flip = (flip, False)

        if hdr_render:
            shader = self._shader_tonemap

        dest_vertices = create_rotated_rect(
            position, section.width, section.height, scale, angle, flip
        )

        section_vertices = [
            (section.x, section.y),
            (section.x + section.width, section.y),
            (section.x, section.y + section.height),
            (section.x + section.width, section.y + section.height),
        ]

        self.render_from_vertices(tex, layer, dest_vertices, section_vertices, shader)

    def render_from_vertices(
        self,
        tex: Texture,
        layer: Layer,
        dest_vertices: list[(float, float)],
        section_vertices: list[(float, float)],
        shader: Shader = None,
    ) -> None:

        if shader is None:
            shader = self._shader_draw

        vertex_coords = [
            to_dest_coords(p, layer.width, layer.height) for p in dest_vertices
        ]

        p1, p2, p3, p4 = vertex_coords
        vertex_data = np.array([p3, p4, p2, p2, p4, p1], dtype=np.float32)

        section_coords = [
            to_source_coords(p, tex.width, tex.height) for p in section_vertices
        ]

        p1, p2, p3, p4 = section_coords
        section_data = np.array([p3, p4, p1, p1, p4, p2], dtype=np.float32)

        buffer_data = np.hstack([vertex_data, section_data])

        vbo = self._ctx.buffer(buffer_data)
        vao = self._ctx.vertex_array(
            shader.program,
            [
                (vbo, '2f 2f', 'vertexPos', 'vertexTexCoord'),
            ],
        )

        tex.use()
        shader.bind_sampler2D_uniforms()

        layer.framebuffer.use()

        vao.render()

        shader.clear_sampler2D_uniforms()

        vbo.release()
        vao.release()

    def render_primitive(
        self,
        layer: Layer,
        color: tuple,
        vertices: list[tuple[float, float]],
        antialias: bool = False,
        mode: int = moderngl.LINES,
    ):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)

        color = [c / 255.0 for c in color]

        if antialias:
            pass

        dest_width, dest_height = layer.size
        dest_vertices = np.array(
            [to_dest_coords(v, dest_width, dest_height) for v in vertices]
        )

        vbo = self.ctx.buffer(dest_vertices.astype('f4').tobytes())
        vao = self.ctx.simple_vertex_array(self.prog_prim, vbo, 'vert')

        self.prog_prim['primColor'] = color

        layer.framebuffer.use()

        vao.render(mode)

        if antialias:
            pass

        vbo.release()
        vao.release()

    def render_triangles(
        self,
        layer: Layer,
        color: tuple,
        vertices: list[tuple[float, float]],
        antialias: bool = False,
        strip: bool = False,
        fan: bool = False,
    ):
        if strip and fan:
            warnings.warn(
                'Both strip and fan flags enabled. Overriding with strip flag.'
            )

        if strip:
            flag = moderngl.TRIANGLE_STRIP
        elif fan:
            flag = moderngl.TRIANGLE_FAN
        else:
            flag = moderngl.TRIANGLES

        self.render_primitive(layer, color, vertices, antialias, flag)

    def render_lines(
        self,
        layer: Layer,
        color: tuple[float, float, float],
        vertices: list[tuple[float, float]],
        antialias: bool = False,
        strip: bool = False,
    ):
        if strip:
            flag = moderngl.LINE_STRIP
        else:
            flag = moderngl.LINES

        self.render_primitive(layer, color, vertices, antialias, flag)

    def render_circle_arc(
        self,
        layer: Layer,
        color: tuple,
        center: tuple[float, float],
        radius: float,
        angle1: float,
        angle2: float,
        antialias: bool = False,
        num_segments: None | int = None,
    ):
        if angle2 < angle1:
            angle2 += 360

        if num_segments is None:
            num_segments = max(4, int(32 * abs(angle2 - angle1) / 360))

        angle1 = np.radians(angle1)
        angle2 = np.radians(angle2)

        vertices = [center]

        for angle in np.linspace(angle1, angle2, num_segments + 1):

            x = center[0] + radius * cos(angle)
            y = center[1] + radius * sin(angle)

            vertices.append((x, y))

        self.render_primitive(layer, color, vertices, antialias, moderngl.TRIANGLE_FAN)

    def render_circle(
        self,
        layer: Layer,
        color: tuple,
        center: tuple[float, float],
        radius: float,
        antialias: bool = False,
        num_segments: int = None,
    ):
        self.render_circle_arc(
            layer, color, center, radius, 0, 360, antialias, num_segments
        )

    def render_rectangle(
        self,
        layer: Layer,
        color: tuple,
        position: tuple[float, float],
        width: float,
        height: float,
        angle: float = 0,
        antialias: bool = False,
    ):
        vertices = create_rotated_rect(
            position, width, height, [1, 1], angle, [False, False]
        )
        v1, v2, v3, v4 = vertices
        self.render_primitive(
            layer, color, [v2, v3, v1, v4], antialias, moderngl.TRIANGLE_STRIP
        )

    def render_thick_line(
        self,
        layer: Layer,
        color: tuple,
        p1: tuple[float, float],
        p2: tuple[float, float],
        thickness: float,
        capped: bool = False,
        antialias: bool = False,
    ):
        direction = (p2[0] - p1[0], p2[1] - p1[1])
        direction_norm = np.linalg.norm(direction)
        direction = direction / direction_norm

        h_thickness = thickness / 2
        perpendicular = np.array([-direction[1], direction[0]]) * h_thickness

        vertices = np.array(
            [
                p1 + perpendicular,
                p1 - perpendicular,
                p2 + perpendicular,
                p2 - perpendicular,
            ]
        )

        self.render_primitive(
            layer, color, vertices, antialias, moderngl.TRIANGLE_STRIP
        )

        if capped:
            angle = np.rad2deg(np.arctan2(direction[1], direction[0]))
            self.render_circle_arc(
                layer, color, p1, h_thickness, angle + 90, angle + 270, antialias
            )
            self.render_circle_arc(
                layer, color, p2, h_thickness, angle - 90, angle + 90
            )

    def render_text(
        self,
        font_atlas: FontAtlas,
        layer: Layer,
        text: str,
        letter_frame: int,
        color: tuple,
        scale: float = 1.0,
        alignment: str = 'left',
        position: tuple = (0.0, 0.0),
        width: float = None,
    ):
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)

        color = [c / 255.0 for c in color]

        vertices = font_atlas.build_vertices(layer.width, layer.height, text, letter_frame=letter_frame, scale=scale, position=position, width=width, alignment=alignment)
        font_atlas.font_texture.use(location=0)

        vbo = self._ctx.buffer(vertices.tobytes())
        vao = self._ctx.vertex_array(
            self._shader_text.program,
            [
                (vbo, '2f 2f', 'vertexPos', 'vertexTexCoord'),
            ],
        )

        self._shader_text.program['textColor'].value = (
            color
        )

        layer.framebuffer.use()

        vao.render(mode=self._ctx.TRIANGLES)

        vbo.release()
        vao.release()

    def release_opengl_resources(self):
        self._shader_draw.release()
        self._screen.framebuffer.release()
        self._ctx.release()

        self._shader_draw = None
        self._screen = None
        self._ctx = None

    def __del__(self):
        if self._ctx is not None:
            self.release_opengl_resources()
