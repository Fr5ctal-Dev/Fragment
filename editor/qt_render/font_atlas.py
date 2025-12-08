from PySide6.QtGui import QFont, QImage, QPainter, QColor
from PySide6.QtCore import Qt, QRect
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Iterable, Optional


@dataclass(frozen=True)
class Glyph:
    size_px: Tuple[int, int]
    uv: Tuple[float, float, float, float]


class FontAtlas:

    CHAR_START = 32
    CHAR_END   = 126
    ATLAS_COLS = 16
    PADDING_PX = 4
    UV_SHRINK  = 0.5

    def __init__(self, engine, font_path: str, font_size: int):
        self.font_size = int(font_size)

        if font_path:
            font_id = QFont.addApplicationFont(font_path)
            if font_id == -1:
                raise ValueError(f'Failed to load font from {font_path}')
            family = QFont.applicationFontFamilies(font_id)[0]
            self.font = QFont(family, self.font_size)
        else:
            self.font = QFont('Arial', self.font_size)

        from PySide6.QtGui import QFontMetrics
        metrics = QFontMetrics(self.font)
        self.ascent = metrics.ascent()
        self.descent = metrics.descent()
        self.linesize = metrics.lineSpacing()
        self.space_advance_px = metrics.horizontalAdvance(' ')

        self.glyphs: Dict[str, Glyph] = {}
        atlas_image = self._build_atlas_image()
        self.font_texture = engine.qimage_to_texture(atlas_image)

    def build_vertices(
        self,
        layer_width: int,
        layer_height: int,
        text: str,
        scale: float = 1.0,
        position: Tuple[float, float] = (0.0, 0.0),
        width: Optional[float] = None,
        alignment: str = 'left',
        letter_frame: Optional[int] = None,
    ) -> np.ndarray:
        if not text:
            return np.zeros((0,), dtype=np.float32)

        if letter_frame is not None:
            if letter_frame < 0:
                return np.zeros((0,), dtype=np.float32)
            text = text[: letter_frame + 1]

        left_ndc, top_ndc = self._pixels_to_ndc(position[0], position[1], layer_width, layer_height)
        box_width_ndc = (
            2.0 * (width / layer_width) if width is not None
            else 1.0 - left_ndc
        )

        def px_w_to_ndc(px: float) -> float:
            return 2.0 * (px / layer_width) * scale

        def px_h_to_ndc(px: float) -> float:
            return 2.0 * (px / layer_height) * scale

        lines: List[List[Tuple[str, float, float]]] = []
        current: List[Tuple[str, float, float]] = []
        line_w = 0.0
        line_h = 0.0

        def commit_line():
            nonlocal current, line_w, line_h
            if current:
                lines.append(current)
                current = []
            line_w = 0.0
            line_h = 0.0

        tokens = FontAtlas._tokenize(text)

        for tok in tokens:
            if tok == '\n':
                commit_line()
                continue

            tok_quads: List[Tuple[str, float, float]] = []
            tok_w = 0.0
            tok_h = 0.0
            for ch in tok:
                g = self.glyphs.get(ch)
                if not g:
                    w_ndc = px_w_to_ndc(self.space_advance_px)
                    h_ndc = px_h_to_ndc(self.linesize)
                else:
                    w_ndc = px_w_to_ndc(g.size_px[0])
                    h_ndc = px_h_to_ndc(g.size_px[1])
                tok_quads.append((ch, w_ndc, h_ndc))
                tok_w += w_ndc
                tok_h = max(tok_h, h_ndc)

            if line_w > 0.0 and (line_w + tok_w) > box_width_ndc:
                commit_line()

            if tok_w > box_width_ndc and len(tok) > 1:
                for ch, w_ndc, h_ndc in tok_quads:
                    if line_w > 0.0 and (line_w + w_ndc) > box_width_ndc:
                        commit_line()
                    current.append((ch, w_ndc, h_ndc))
                    line_w += w_ndc
                    line_h = max(line_h, h_ndc)
            else:
                for ch, w_ndc, h_ndc in tok_quads:
                    current.append((ch, w_ndc, h_ndc))
                line_w += tok_w
                line_h = max(line_h, tok_h)

        commit_line()

        verts: List[float] = []
        y = top_ndc
        for line in lines:
            lw = sum(w for _, w, _ in line)
            lh = max((h for _, _, h in line), default=0.0)

            x = self._aligned_start_x(left_ndc, box_width_ndc, lw, alignment)

            for ch, w, h in line:
                g = self.glyphs.get(ch)
                if not g:
                    x += w
                    continue

                u1, v1, u2, v2 = g.uv

                verts.extend([
                    x,     y - h, u1, v2,
                    x + w, y - h, u2, v2,
                    x,     y,     u1, v1,

                    x,     y,     u1, v1,
                    x + w, y - h, u2, v2,
                    x + w, y,     u2, v1,
                ])

                x += w

            y -= lh

        return np.asarray(verts, dtype=np.float32)

    def _build_atlas_image(self) -> QImage:
        from PySide6.QtGui import QFontMetrics

        metrics = QFontMetrics(self.font)
        widest = max(metrics.horizontalAdvance('M'), metrics.horizontalAdvance('W'), metrics.horizontalAdvance('@'))
        max_height = self.ascent + abs(self.descent)
        cell_w = widest + 2 * self.PADDING_PX
        cell_h = max_height + 2 * self.PADDING_PX

        cols = self.ATLAS_COLS
        num_chars = self.CHAR_END - self.CHAR_START + 1
        rows = (num_chars + cols - 1) // cols

        atlas_w = cols * cell_w
        atlas_h = rows * cell_h

        img = QImage(atlas_w, atlas_h, QImage.Format_RGBA8888)
        img.fill(Qt.transparent)

        painter = QPainter(img)
        painter.setFont(self.font)
        painter.setPen(QColor(255, 255, 255))

        for i, code in enumerate(range(self.CHAR_START, self.CHAR_END + 1)):
            ch = chr(code)

            col = i % cols
            row = i // cols
            x_px = col * cell_w + self.PADDING_PX
            y_px = row * cell_h + self.PADDING_PX

            painter.drawText(x_px, y_px + self.ascent, ch)

            gw = metrics.horizontalAdvance(ch)
            gh = metrics.height()

            u1 = (x_px + self.UV_SHRINK) / atlas_w
            v1 = 1.0 - (y_px + self.UV_SHRINK) / atlas_h
            u2 = (x_px + gw - self.UV_SHRINK) / atlas_w
            v2 = 1.0 - (y_px + gh - self.UV_SHRINK) / atlas_h

            self.glyphs[ch] = Glyph(size_px=(gw, gh), uv=(u1, v1, u2, v2))

        painter.end()
        return img

    @staticmethod
    def _pixels_to_ndc(x_px: float, y_px: float, layer_w: int, layer_h: int) -> Tuple[float, float]:
        x_ndc = -1.0 + 2.0 * (x_px / layer_w)
        y_ndc =  1.0 - 2.0 * (y_px / layer_h)
        return x_ndc, y_ndc

    @staticmethod
    def _aligned_start_x(left: float, box_w: float, line_w: float, alignment: str) -> float:
        a = alignment.lower()
        if a == 'center':
            return left + max(0.0, (box_w - line_w) * 0.5)
        if a == 'right':
            return left + max(0.0, (box_w - line_w))
        return left

    @staticmethod
    def _tokenize(s: str) -> Iterable[str]:
        if not s:
            return []

        tokens: List[str] = []
        buf: List[str] = []
        mode: Optional[str] = None

        def flush():
            nonlocal buf, mode
            if buf:
                tokens.append(''.join(buf))
                buf = []
                mode = None

        for ch in s:
            if ch == '\n':
                flush()
                tokens.append('\n')
                continue
            if ch.isspace():
                if mode != 'space':
                    flush()
                    mode = 'space'
                buf.append(ch)
            else:
                if mode != 'word':
                    flush()
                    mode = 'word'
                buf.append(ch)

        flush()
        return tokens
