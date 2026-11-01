# ui.py
import pygame
import math
from config import (
    WIDTH,
    BOARD_X,
    BOARD_Y,
    BOARD_SIZE,
    PLAY_X,
    PLAY_Y,
    PLAY_SIZE,
    CENTER_X,
    CENTER_Y,
    STRIKER_RADIUS,
    GOLD,
    WHITE_COIN,
    BLACK_COIN,
    QUEEN_COIN,
    RED_ACCENT,
)
from font_renderer import get_font


class GameUI:
    def __init__(self):
        self.font_lg = get_font("Segoe UI", 28, bold=True)
        self.font_md = get_font("Segoe UI", 18, bold=True)
        self.font_sm = get_font("Segoe UI", 14)

    def _blit_aligned(self, screen, text, font, color, x, y, align="left"):
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if align == "center":
            rect.centerx = int(x)
            rect.top = int(y)
        elif align == "right":
            rect.right = int(x)
            rect.top = int(y)
        elif align == "midleft":
            rect.left = int(x)
            rect.centery = int(y)
        elif align == "midright":
            rect.right = int(x)
            rect.centery = int(y)
        else:
            rect.topleft = (int(x), int(y))
        screen.blit(surf, rect)
        return rect

    def draw_aim_guide(self, screen, striker, coins, aim_pos):
        mx, my = aim_pos
        dx = striker.x - mx
        dy = striker.y - my
        dist = math.hypot(dx, dy)

        if dist < 6:
            return

        power_ratio = min(1.0, dist / 200.0)
        ux = dx / dist
        uy = dy / dist

        # Power ring around striker
        ring_r = int(STRIKER_RADIUS + 6 + 18 * power_ratio)
        ring_col = (
            int(60 + 195 * power_ratio),
            int(220 - 150 * power_ratio),
            65,
        )
        ring_surf = pygame.Surface((ring_r * 2 + 6, ring_r * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(
            ring_surf, (*ring_col, 130), (ring_r + 3, ring_r + 3), ring_r, 2
        )
        screen.blit(ring_surf, (int(striker.x - ring_r - 3), int(striker.y - ring_r - 3)))

        # Pullback band
        pygame.draw.aaline(screen, (210, 220, 235), (striker.x, striker.y), (mx, my))
        pygame.draw.circle(screen, ring_col, (int(round(mx)), int(round(my))), 6)
        pygame.draw.circle(screen, (255, 255, 255), (int(round(mx)), int(round(my))), 3)

        # Raycast forward to find first coin or wall collision
        ray_len = 520 * power_ratio + 50
        closest_t = ray_len
        hit_coin = None

        # Check wall boundaries along ray
        min_x = PLAY_X + STRIKER_RADIUS
        max_x = PLAY_X + PLAY_SIZE - STRIKER_RADIUS
        min_y = PLAY_Y + STRIKER_RADIUS
        max_y = PLAY_Y + PLAY_SIZE - STRIKER_RADIUS

        if ux < -1e-5:
            closest_t = min(closest_t, (min_x - striker.x) / ux)
        elif ux > 1e-5:
            closest_t = min(closest_t, (max_x - striker.x) / ux)
        if uy < -1e-5:
            closest_t = min(closest_t, (min_y - striker.y) / uy)
        elif uy > 1e-5:
            closest_t = min(closest_t, (max_y - striker.y) / uy)

        for c in coins:
            if c.pocketing:
                continue
            fx = c.x - striker.x
            fy = c.y - striker.y
            proj = fx * ux + fy * uy
            if proj > 0:
                perp_sq = (fx * fx + fy * fy) - proj * proj
                combined_r = STRIKER_RADIUS + c.radius
                if perp_sq < combined_r * combined_r:
                    t = proj - math.sqrt(combined_r * combined_r - perp_sq)
                    if 0 < t < closest_t:
                        closest_t = t
                        hit_coin = c

        # Smooth anti-aliased laser guide line + spaced nodes
        end_gx = striker.x + ux * closest_t
        end_gy = striker.y + uy * closest_t
        pygame.draw.aaline(screen, (255, 245, 200), (striker.x, striker.y), (end_gx, end_gy))

        steps = int(closest_t // 22)
        for i in range(1, steps + 1):
            px = int(round(striker.x + ux * (i * 22)))
            py = int(round(striker.y + uy * (i * 22)))
            pygame.draw.circle(screen, GOLD, (px, py), 2)

        # Ghost striker & deflection vector at impact
        if hit_coin:
            gx = striker.x + ux * closest_t
            gy = striker.y + uy * closest_t
            ghost_s = pygame.Surface((STRIKER_RADIUS * 2 + 4, STRIKER_RADIUS * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                ghost_s, (255, 255, 255, 130), (STRIKER_RADIUS + 2, STRIKER_RADIUS + 2), STRIKER_RADIUS, 2
            )
            screen.blit(ghost_s, (int(round(gx - STRIKER_RADIUS - 2)), int(round(gy - STRIKER_RADIUS - 2))))

            nx = hit_coin.x - gx
            ny = hit_coin.y - gy
            nd = math.hypot(nx, ny)
            if nd > 0:
                nx /= nd
                ny /= nd
                end_x = hit_coin.x + nx * (110 * power_ratio + 25)
                end_y = hit_coin.y + ny * (110 * power_ratio + 25)
                pygame.draw.aaline(screen, GOLD, (hit_coin.x, hit_coin.y), (end_x, end_y))
                pygame.draw.circle(screen, GOLD, (int(round(end_x)), int(round(end_y))), 4)

    def draw_hud(self, screen, game, aim_pos):
        panel_x = BOARD_X + BOARD_SIZE + 25
        panel_w = WIDTH - panel_x - 25
        panel_cx = panel_x + panel_w // 2

        # Outer Dashboard Card
        pygame.draw.rect(screen, (26, 29, 38), (panel_x, BOARD_Y, panel_w, BOARD_SIZE), border_radius=18)
        pygame.draw.rect(screen, (52, 58, 74), (panel_x, BOARD_Y, panel_w, BOARD_SIZE), 2, border_radius=18)

        # Top Header Banner
        header_rect = (panel_x + 12, BOARD_Y + 12, panel_w - 24, 68)
        pygame.draw.rect(screen, (34, 38, 50), header_rect, border_radius=12)
        self._blit_aligned(screen, "CARROM MASTER", self.font_md, GOLD, panel_cx, BOARD_Y + 22, "center")
        self._blit_aligned(screen, "2D PHYSICS EDITION", self.font_sm, (150, 160, 180), panel_cx, BOARD_Y + 50, "center")

        # Remaining Coins Count
        white_rem = sum(1 for c in game.coins if c.disc_type == "white" and not c.pocketing)
        black_rem = sum(1 for c in game.coins if c.disc_type == "black" and not c.pocketing)

        # Player Cards
        players = [
            ("PLAYER 1", "WHITE COINS", WHITE_COIN, game.scores[0], white_rem, game.turn == 0, BOARD_Y + 94),
            ("PLAYER 2", "BLACK COINS", BLACK_COIN, game.scores[1], black_rem, game.turn == 1, BOARD_Y + 222),
        ]

        for p_title, p_sub, col, score, rem, active, py in players:
            card_w = panel_w - 28
            card_h = 114
            cx = panel_x + 14

            bg_col = (42, 48, 64) if active else (22, 25, 33)
            border_col = GOLD if active else (42, 46, 58)
            pygame.draw.rect(screen, bg_col, (cx, py, card_w, card_h), border_radius=14)
            pygame.draw.rect(screen, border_col, (cx, py, card_w, card_h), 2, border_radius=14)

            # Active Turn Badge
            if active:
                badge_rect = (cx + card_w - 74, py + 10, 62, 20)
                pygame.draw.rect(screen, GOLD, badge_rect, border_radius=6)
                self._blit_aligned(screen, "TURN", self.font_sm, (20, 22, 28), cx + card_w - 43, py + 13, "center")

            # Coin Icon
            pygame.draw.circle(screen, col, (cx + 26, py + 28), 12)
            pygame.draw.circle(screen, GOLD if active else (110, 115, 130), (cx + 26, py + 28), 12, 2)

            # Player Name & Subtitle
            self._blit_aligned(screen, p_title, self.font_md, (245, 245, 250), cx + 46, py + 14, "left")
            self._blit_aligned(screen, p_sub, self.font_sm, (150, 158, 175), cx + 46, py + 36, "left")

            # Divider Line
            pygame.draw.line(screen, (55, 62, 78), (cx + 14, py + 58), (cx + card_w - 14, py + 58), 1)

            # Bottom Row: Score & Remaining Coins
            self._blit_aligned(screen, "SCORE", self.font_sm, (165, 172, 190), cx + 16, py + 68, "left")
            self._blit_aligned(screen, str(score), self.font_lg, GOLD if active else (210, 215, 225), cx + 16, py + 84, "left")

            self._blit_aligned(screen, f"LEFT: {rem}", self.font_sm, (175, 182, 200), cx + card_w - 16, py + 88, "right")

        # Queen Status Card
        qy = BOARD_Y + 350
        qw = panel_w - 28
        qx = panel_x + 14
        pygame.draw.rect(screen, (22, 25, 33), (qx, qy, qw, 74), border_radius=12)
        pygame.draw.rect(screen, (45, 50, 64), (qx, qy, qw, 74), 2, border_radius=12)

        pygame.draw.circle(screen, QUEEN_COIN, (qx + 24, qy + 24), 10)
        pygame.draw.circle(screen, GOLD, (qx + 24, qy + 24), 4)
        self._blit_aligned(screen, "RED QUEEN (+3)", self.font_sm, QUEEN_COIN, qx + 42, qy + 17, "left")

        if game.queen_covered_by is not None:
            q_status = f"COVERED BY P{game.queen_covered_by + 1}"
            q_col = GOLD
        elif game.queen_holder is not None:
            q_status = f"P{game.queen_holder + 1}: COVER NOW!"
            q_col = (255, 115, 115)
        else:
            q_status = "ON THE BOARD"
            q_col = (200, 205, 215)

        self._blit_aligned(screen, q_status, self.font_md, q_col, qx + 16, qy + 44, "left")

        # Shot Power Meter Card
        pmy = BOARD_Y + 438
        pygame.draw.rect(screen, (22, 25, 33), (qx, pmy, qw, 70), border_radius=12)
        pygame.draw.rect(screen, (45, 50, 64), (qx, pmy, qw, 70), 2, border_radius=12)

        dist = math.hypot(game.striker.x - aim_pos[0], game.striker.y - aim_pos[1]) if game.state == "AIMING" else 0.0
        ratio = min(1.0, dist / 200.0)
        pct = int(round(ratio * 100))

        self._blit_aligned(screen, "SHOT POWER", self.font_sm, (175, 182, 200), qx + 14, pmy + 12, "left")
        self._blit_aligned(screen, f"{pct}%", self.font_sm, GOLD if pct > 0 else (130, 135, 150), qx + qw - 14, pmy + 12, "right")

        bar_x, bar_y, bar_w, bar_h = qx + 14, pmy + 36, qw - 28, 18
        pygame.draw.rect(screen, (14, 16, 22), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
        if ratio > 0:
            fill_w = max(6, int(bar_w * ratio))
            bar_color = (int(60 + 195 * ratio), int(220 - 160 * ratio), 55)
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, fill_w, bar_h), border_radius=8)
        pygame.draw.rect(screen, (60, 66, 82), (bar_x, bar_y, bar_w, bar_h), 1, border_radius=8)

        # Controls Card
        cy = BOARD_Y + 522
        ch = 152
        pygame.draw.rect(screen, (22, 25, 33), (qx, cy, qw, ch), border_radius=12)
        pygame.draw.rect(screen, (45, 50, 64), (qx, cy, qw, ch), 2, border_radius=12)

        self._blit_aligned(screen, "CONTROLS", self.font_sm, GOLD, qx + 14, cy + 12, "left")
        controls = [
            ("MOUSE", "SLIDE STRIKER"),
            ("L-CLICK", "LOCK POSITION"),
            ("DRAG", "AIM & SHOOT"),
            ("R-CLICK", "CANCEL AIM"),
            ("KEY R", "RESET MATCH"),
        ]
        for i, (k_txt, v_txt) in enumerate(controls):
            ry = cy + 36 + i * 22
            self._blit_aligned(screen, k_txt, self.font_sm, (215, 220, 230), qx + 14, ry, "left")
            self._blit_aligned(screen, v_txt, self.font_sm, (145, 152, 170), qx + qw - 14, ry, "right")

        # Bottom Status Pill
        by = BOARD_Y + BOARD_SIZE - 52
        pygame.draw.rect(screen, (36, 42, 56), (qx, by, qw, 38), border_radius=10)
        pygame.draw.rect(screen, GOLD, (qx, by, qw, 38), 1, border_radius=10)

        state_str = {
            "PLACE_STRIKER": "SLIDE & CLICK STRIKER",
            "AIMING": "PULL BACK & RELEASE!",
            "SIMULATING": "SHOT IN PROGRESS...",
            "GAME_OVER": "MATCH OVER! PRESS R",
        }[game.state]
        self._blit_aligned(screen, state_str, self.font_sm, GOLD, panel_cx, by + 12, "center")

    def draw_game_over(self, screen, winner_text):
        overlay = pygame.Surface((BOARD_SIZE - 80, 150), pygame.SRCALPHA)
        overlay.fill((14, 16, 22, 235))
        ox = BOARD_X + 40
        oy = CENTER_Y - 75
        screen.blit(overlay, (ox, oy))
        pygame.draw.rect(screen, GOLD, (ox, oy, BOARD_SIZE - 80, 150), 3, border_radius=16)

        self._blit_aligned(screen, winner_text, self.font_lg, GOLD, CENTER_X, CENTER_Y - 32, "center")
        self._blit_aligned(screen, "PRESS 'R' TO PLAY AGAIN", self.font_md, WHITE_COIN, CENTER_X, CENTER_Y + 22, "center")
