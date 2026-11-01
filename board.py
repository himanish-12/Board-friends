# board.py
import pygame
import math
from config import (
    BOARD_SIZE,
    BOARD_X,
    BOARD_Y,
    BORDER_THICKNESS,
    PLAY_X,
    PLAY_Y,
    PLAY_SIZE,
    POCKET_RADIUS,
    WOOD_DARK,
    WOOD_MID,
    WOOD_SURFACE,
    WOOD_SURFACE_ALT,
    LINE_COLOR,
    RED_ACCENT,
    POCKET_COLOR,
    GOLD,
)


class CarromBoard:
    def __init__(self):
        inset = POCKET_RADIUS + 6
        self.pockets = [
            (PLAY_X + inset, PLAY_Y + inset),
            (PLAY_X + PLAY_SIZE - inset, PLAY_Y + inset),
            (PLAY_X + inset, PLAY_Y + PLAY_SIZE - inset),
            (PLAY_X + PLAY_SIZE - inset, PLAY_Y + PLAY_SIZE - inset),
        ]
        self.surface = self._create_board_surface()

    def get_baseline_y(self, turn):
        margin = 95
        line_gap = 26
        if turn == 0:
            return PLAY_Y + PLAY_SIZE - margin - line_gap // 2
        return PLAY_Y + margin + line_gap // 2

    def _create_board_surface(self):
        surf = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        surf.fill(WOOD_DARK)

        # Outer frame bevels
        pygame.draw.rect(surf, WOOD_MID, (8, 8, BOARD_SIZE - 16, BOARD_SIZE - 16), border_radius=28)
        pygame.draw.rect(surf, WOOD_DARK, (14, 14, BOARD_SIZE - 28, BOARD_SIZE - 28), 4, border_radius=24)

        # Playing surface
        bt = BORDER_THICKNESS
        ps = PLAY_SIZE
        pygame.draw.rect(surf, WOOD_SURFACE, (bt, bt, ps, ps), border_radius=14)
        pygame.draw.rect(surf, LINE_COLOR, (bt, bt, ps, ps), 3, border_radius=14)

        cx, cy = BOARD_SIZE // 2, BOARD_SIZE // 2

        # Center Mandala Star & Circles
        pygame.draw.circle(surf, WOOD_SURFACE_ALT, (cx, cy), 76)
        pygame.draw.circle(surf, LINE_COLOR, (cx, cy), 76, 2)
        pygame.draw.circle(surf, RED_ACCENT, (cx, cy), 62, 1)

        for i in range(8):
            angle = i * (math.pi / 4)
            next_angle = angle + (math.pi / 8)
            prev_angle = angle - (math.pi / 8)
            tip = (cx + math.cos(angle) * 72, cy + math.sin(angle) * 72)
            left = (cx + math.cos(prev_angle) * 26, cy + math.sin(prev_angle) * 26)
            right = (cx + math.cos(next_angle) * 26, cy + math.sin(next_angle) * 26)
            color = RED_ACCENT if i % 2 == 0 else LINE_COLOR
            pygame.draw.polygon(surf, color, [(cx, cy), left, tip, right])

        pygame.draw.circle(surf, WOOD_SURFACE, (cx, cy), 20)
        pygame.draw.circle(surf, RED_ACCENT, (cx, cy), 17)
        pygame.draw.circle(surf, LINE_COLOR, (cx, cy), 20, 2)

        # 4 Striker Baselines
        margin = 95
        line_gap = 26
        span = ps // 2 - 115

        baselines = [
            ((cx - span, bt + ps - margin), (cx + span, bt + ps - margin),
             (cx - span, bt + ps - margin - line_gap), (cx + span, bt + ps - margin - line_gap)),
            ((cx - span, bt + margin), (cx + span, bt + margin),
             (cx - span, bt + margin + line_gap), (cx + span, bt + margin + line_gap)),
            ((bt + margin, cy - span), (bt + margin, cy + span),
             (bt + margin + line_gap, cy - span), (bt + margin + line_gap, cy + span)),
            ((bt + ps - margin, cy - span), (bt + ps - margin, cy + span),
             (bt + ps - margin - line_gap, cy - span), (bt + ps - margin - line_gap, cy + span)),
        ]

        for l1_start, l1_end, l2_start, l2_end in baselines:
            pygame.draw.line(surf, LINE_COLOR, l1_start, l1_end, 3)
            pygame.draw.line(surf, LINE_COLOR, l2_start, l2_end, 1)

            for pt1, pt2 in [(l1_start, l2_start), (l1_end, l2_end)]:
                mid_x = (pt1[0] + pt2[0]) // 2
                mid_y = (pt1[1] + pt2[1]) // 2
                pygame.draw.circle(surf, RED_ACCENT, (mid_x, mid_y), line_gap // 2)
                pygame.draw.circle(surf, LINE_COLOR, (mid_x, mid_y), line_gap // 2, 2)

        # Diagonal foul arrows
        diag_offset = 78
        diag_len = 140
        corners = [
            (bt + diag_offset, bt + diag_offset, 1, 1),
            (bt + ps - diag_offset, bt + diag_offset, -1, 1),
            (bt + diag_offset, bt + ps - diag_offset, 1, -1),
            (bt + ps - diag_offset, bt + ps - diag_offset, -1, -1),
        ]
        for sx, sy, dx, dy in corners:
            ex = sx + dx * diag_len
            ey = sy + dy * diag_len
            pygame.draw.line(surf, LINE_COLOR, (sx, sy), (ex, ey), 2)
            pygame.draw.circle(surf, LINE_COLOR, (ex, ey), 22, 2)

        # Corner Pockets
        inset = POCKET_RADIUS + 6
        local_pockets = [
            (bt + inset, bt + inset),
            (bt + ps - inset, bt + inset),
            (bt + inset, bt + ps - inset),
            (bt + ps - inset, bt + ps - inset),
        ]
        for px, py in local_pockets:
            pygame.draw.circle(surf, (45, 30, 18), (px, py), POCKET_RADIUS + 4)
            pygame.draw.circle(surf, POCKET_COLOR, (px, py), POCKET_RADIUS)
            pygame.draw.circle(surf, (38, 38, 44), (px, py), POCKET_RADIUS - 4, 2)

        return surf

    def draw(self, screen, shake_offset=(0, 0)):
        screen.blit(self.surface, (BOARD_X + shake_offset[0], BOARD_Y + shake_offset[1]))

    def draw_active_baseline(self, screen, turn, min_x, max_x, shake_offset=(0, 0)):
        by = int(self.get_baseline_y(turn) + shake_offset[1])
        pygame.draw.line(screen, GOLD, (int(min_x), by), (int(max_x), by), 3)