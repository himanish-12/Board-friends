# board.py
import pygame
import math
from settings import (
    BOARD_SIZE,
    BOARD_X,
    BOARD_Y,
    FRAME_WIDTH,
    PLAY_X,
    PLAY_Y,
    PLAY_SIZE,
    POCKET_R,
    FRAME_OUTER,
    FRAME_INNER,
    BRASS,
    BOARD_WOOD,
    BOARD_WOOD_DARK,
    INK_LINE,
    CRIMSON,
    POCKET_HOLE,
    POCKET_NET,
    GOLD,
)


class CarromBoard:
    def __init__(self):
        inset = POCKET_R + 6
        self.pockets = [
            (PLAY_X + inset, PLAY_Y + inset),
            (PLAY_X + PLAY_SIZE - inset, PLAY_Y + inset),
            (PLAY_X + inset, PLAY_Y + PLAY_SIZE - inset),
            (PLAY_X + PLAY_SIZE - inset, PLAY_Y + PLAY_SIZE - inset),
        ]
        self.cached_board = self._bake_board_surface()

    def baseline_y_for(self, player_idx):
        margin = 95
        gap = 26
        if player_idx == 0:
            return PLAY_Y + PLAY_SIZE - margin - gap // 2
        return PLAY_Y + margin + gap // 2

    def _bake_board_surface(self):
        surf = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
        surf.fill(FRAME_OUTER)

        # Classic Rosewood outer frame + brass corner rivets
        pygame.draw.rect(surf, FRAME_INNER, (8, 8, BOARD_SIZE - 16, BOARD_SIZE - 16), border_radius=28)
        pygame.draw.rect(surf, (48, 26, 14), (14, 14, BOARD_SIZE - 28, BOARD_SIZE - 28), 4, border_radius=24)

        rivet_pts = [
            (28, 28), (BOARD_SIZE - 28, 28),
            (28, BOARD_SIZE - 28), (BOARD_SIZE - 28, BOARD_SIZE - 28)
        ]
        for rx, ry in rivet_pts:
            pygame.draw.circle(surf, BRASS, (rx, ry), 5)
            pygame.draw.circle(surf, (120, 88, 30), (rx, ry), 5, 1)

        # Warm Birchwood playing field
        fw = FRAME_WIDTH
        ps = PLAY_SIZE
        pygame.draw.rect(surf, BOARD_WOOD, (fw, fw, ps, ps), border_radius=14)
        pygame.draw.rect(surf, INK_LINE, (fw, fw, ps, ps), 3, border_radius=14)

        cx, cy = BOARD_SIZE // 2, BOARD_SIZE // 2

        # Traditional Center Lotus Mandala
        pygame.draw.circle(surf, BOARD_WOOD_DARK, (cx, cy), 76)
        pygame.draw.circle(surf, INK_LINE, (cx, cy), 76, 2)
        pygame.draw.circle(surf, CRIMSON, (cx, cy), 62, 1)

        for i in range(8):
            ang = i * (math.pi / 4)
            l_ang = ang - (math.pi / 8)
            r_ang = ang + (math.pi / 8)
            tip = (cx + math.cos(ang) * 72, cy + math.sin(ang) * 72)
            left = (cx + math.cos(l_ang) * 26, cy + math.sin(l_ang) * 26)
            right = (cx + math.cos(r_ang) * 26, cy + math.sin(r_ang) * 26)
            petal_col = CRIMSON if i % 2 == 0 else INK_LINE
            pygame.draw.polygon(surf, petal_col, [(cx, cy), left, tip, right])

        pygame.draw.circle(surf, BOARD_WOOD, (cx, cy), 20)
        pygame.draw.circle(surf, CRIMSON, (cx, cy), 16)
        pygame.draw.circle(surf, INK_LINE, (cx, cy), 20, 2)

        # Four striker baselines with crimson end-circles
        margin = 95
        gap = 26
        span = ps // 2 - 115

        lines = [
            ((cx - span, fw + ps - margin), (cx + span, fw + ps - margin),
             (cx - span, fw + ps - margin - gap), (cx + span, fw + ps - margin - gap)),
            ((cx - span, fw + margin), (cx + span, fw + margin),
             (cx - span, fw + margin + gap), (cx + span, fw + margin + gap)),
            ((fw + margin, cy - span), (fw + margin, cy + span),
             (fw + margin + gap, cy - span), (fw + margin + gap, cy + span)),
            ((fw + ps - margin, cy - span), (fw + ps - margin, cy + span),
             (fw + ps - margin - gap, cy - span), (fw + ps - margin - gap, cy + span)),
        ]

        for l1_a, l1_b, l2_a, l2_b in lines:
            pygame.draw.line(surf, INK_LINE, l1_a, l1_b, 3)
            pygame.draw.line(surf, INK_LINE, l2_a, l2_b, 1)

            for p1, p2 in [(l1_a, l2_a), (l1_b, l2_b)]:
                mx = (p1[0] + p2[0]) // 2
                my = (p1[1] + p2[1]) // 2
                r_end = gap // 2
                pygame.draw.circle(surf, CRIMSON, (mx, my), r_end)
                pygame.draw.circle(surf, BOARD_WOOD, (mx, my), 4)
                pygame.draw.circle(surf, INK_LINE, (mx, my), r_end, 2)

        # Diagonal foul lines
        d_off = 78
        d_len = 140
        diags = [
            (fw + d_off, fw + d_off, 1, 1),
            (fw + ps - d_off, fw + d_off, -1, 1),
            (fw + d_off, fw + ps - d_off, 1, -1),
            (fw + ps - d_off, fw + ps - d_off, -1, -1),
        ]
        for sx, sy, dx, dy in diags:
            ex = sx + dx * d_len
            ey = sy + dy * d_len
            pygame.draw.line(surf, INK_LINE, (sx, sy), (ex, ey), 2)
            pygame.draw.circle(surf, INK_LINE, (ex, ey), 22, 2)

        # Corner pockets
        inset = POCKET_R + 6
        corners = [
            (fw + inset, fw + inset),
            (fw + ps - inset, fw + inset),
            (fw + inset, fw + ps - inset),
            (fw + ps - inset, fw + ps - inset),
        ]
        for px, py in corners:
            pygame.draw.circle(surf, (46, 30, 18), (px, py), POCKET_R + 4)
            pygame.draw.circle(surf, POCKET_HOLE, (px, py), POCKET_R)
            pygame.draw.circle(surf, POCKET_NET, (px, py), POCKET_R - 5, 1)
            pygame.draw.circle(surf, (28, 25, 22), (px, py), POCKET_R - 12, 1)

        return surf

    def draw(self, screen, shake=(0, 0)):
        screen.blit(self.cached_board, (BOARD_X + shake[0], BOARD_Y + shake[1]))

    def highlight_active_lane(self, screen, turn, min_x, max_x, shake=(0, 0)):
        by = int(self.baseline_y_for(turn) + shake[1])
        glow_w = int(max_x - min_x + 20)
        glow = pygame.Surface((glow_w, 16), pygame.SRCALPHA)
        pygame.draw.line(glow, (*GOLD, 65), (10, 8), (glow_w - 10, 8), 8)
        screen.blit(glow, (int(min_x - 10), by - 8))
        pygame.draw.line(screen, GOLD, (int(min_x), by), (int(max_x), by), 3)
