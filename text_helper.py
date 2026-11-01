# text_helper.py
import pygame
import math
from settings import CANDY_TOP, CANDY_BOT, CANDY_OUTLINE, CANDY_HIGHLIGHT

# Proportional 5x7 bitmap fallback
GLYPHS = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01111", "10000", "10000", "10000", "10000", "10000", "01111"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01111", "10000", "10000", "10011", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["111", "010", "010", "010", "010", "010", "111"],
    'J': ["00111", "00010", "00010", "00010", "10010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["010", "110", "010", "010", "010", "010", "111"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11110", "00001", "00001", "01110", "00001", "00001", "11110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "10000", "11110", "00001", "00001", "11110"],
    '6': ["01110", "10000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00001", "01110"],
    ':': ["0", "1", "1", "0", "1", "1", "0"],
    '.': ["0", "0", "0", "0", "0", "1", "1"],
    '!': ["1", "1", "1", "1", "1", "0", "1"],
    '+': ["00000", "00100", "00100", "11111", "00100", "00100", "00000"],
    '-': ["0000", "0000", "0000", "1111", "0000", "0000", "0000"],
    '/': ["00001", "00010", "00100", "00100", "01000", "10000", "10000"],
    '%': ["11001", "11010", "00100", "00100", "01011", "10011", "00000"],
    '(': ["01", "10", "10", "10", "10", "10", "01"],
    ')': ["10", "01", "01", "01", "01", "01", "10"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    "'": ["1", "1", "0", "0", "0", "0", "0"],
    ' ': ["000", "000", "000", "000", "000", "000", "000"],
}

_CANDY_CACHE = {}


class PixelFont:
    def __init__(self, size=20, bold=False, italic=False):
        if size >= 28:
            self.scale = 3
        elif size >= 15:
            self.scale = 2
        else:
            self.scale = 1
        self.bold = bold and self.scale >= 2

    def render(self, text, antialias, color):
        text_u = str(text).upper()
        s = self.scale
        gap = max(1, s)
        extra = 1 if self.bold else 0

        widths = [len(GLYPHS.get(ch, GLYPHS[' '])[0]) * s + extra for ch in text_u]
        total_w = max(1, sum(widths) + gap * max(0, len(text_u) - 1))
        total_h = 7 * s

        surf = pygame.Surface((total_w + 2, total_h + 2), pygame.SRCALPHA)

        cursor_x = 0
        for idx, ch in enumerate(text_u):
            pattern = GLYPHS.get(ch, GLYPHS[' '])
            for r, row in enumerate(pattern):
                for c, bit in enumerate(row):
                    if bit == '1':
                        pygame.draw.rect(
                            surf, (8, 8, 10, 140), (cursor_x + c * s + 1, r * s + 1, s + extra, s)
                        )
                        pygame.draw.rect(
                            surf, color, (cursor_x + c * s, r * s, s + extra, s)
                        )
            cursor_x += widths[idx] + gap
        return surf


def load_font(size, bold=False):
    # Clean Chess.com style UI font
    try:
        import pygame.font
        if not pygame.font.get_init():
            pygame.font.init()
        return pygame.font.SysFont("Montserrat, Inter, Cantarell, DejaVu Sans, Segoe UI, Arial", size, bold=bold)
    except Exception:
        return PixelFont(size, bold=bold)


def load_candy_font(size):
    # Rounded, bouncy italic/bold font for the Sodalicious / Candy Crush style game text
    try:
        import pygame.font
        if not pygame.font.get_init():
            pygame.font.init()
        return pygame.font.SysFont(
            "Cooper Black, Fredoka One, Lobster, Georgia,URW Bookman, DejaVu Serif, Segoe UI",
            size,
            bold=True,
            italic=True,
        )
    except Exception:
        return PixelFont(size, bold=True)


def render_candy_text(
    text,
    size=26,
    top_color=CANDY_TOP,
    bot_color=CANDY_BOT,
    outline_color=CANDY_OUTLINE,
):
    """
    Renders glossy, 3D 'Sodalicious!' style game text with:
    - Thick dark-brown rounded stroke outline & drop shadow
    - Golden-yellow to rich orange vertical gradient fill
    - Specular top-edge glossy highlight
    """
    cache_key = (str(text), size, top_color, bot_color, outline_color)
    if cache_key in _CANDY_CACHE:
        return _CANDY_CACHE[cache_key]

    font = load_candy_font(size)
    base_white = font.render(str(text), True, (255, 255, 255))
    tw, th = base_white.get_size()

    if tw <= 1 or th <= 1:
        return base_white

    outline_surf = font.render(str(text), True, outline_color)
    highlight_surf = font.render(str(text), True, CANDY_HIGHLIGHT)

    # Create vertical yellow-to-orange gradient and multiply with white text mask
    grad_fill = base_white.copy()
    grad_strip = pygame.Surface((tw, th), pygame.SRCALPHA)
    for y in range(th):
        # Smooth S-curve gradient for extra candy pop
        t = y / max(1, th - 1)
        t_curved = t * t * (3 - 2 * t)
        r = int(top_color[0] + (bot_color[0] - top_color[0]) * t_curved)
        g = int(top_color[1] + (bot_color[1] - top_color[1]) * t_curved)
        b = int(top_color[2] + (bot_color[2] - top_color[2]) * t_curved)
        pygame.draw.line(grad_strip, (r, g, b, 255), (0, y), (tw, y))

    grad_fill.blit(grad_strip, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    border = max(3, size // 7)
    drop_y = max(2, border // 2 + 1)
    pad = border + drop_y + 3
    final_surf = pygame.Surface((tw + pad * 2, th + pad * 2), pygame.SRCALPHA)

    # 1. Extruded 3D bottom drop shadow in dark chocolate brown
    for dy_extra in range(1, drop_y + 1):
        for dx in range(-border, border + 1):
            for dy in range(-border, border + 1):
                if dx * dx + dy * dy <= border * border:
                    final_surf.blit(outline_surf, (pad + dx, pad + dy + dy_extra))

    # 2. Thick rounded outer stroke
    for dx in range(-border, border + 1):
        for dy in range(-border, border + 1):
            if dx * dx + dy * dy <= border * border:
                final_surf.blit(outline_surf, (pad + dx, pad + dy))

    # 3. Glossy upper-rim inner highlight
    highlight_surf.set_alpha(150)
    final_surf.blit(highlight_surf, (pad, pad - 1))

    # 4. Main golden-orange gradient body
    final_surf.blit(grad_fill, (pad, pad))

    if len(_CANDY_CACHE) > 120:
        _CANDY_CACHE.clear()
    _CANDY_CACHE[cache_key] = final_surf
    return final_surf
