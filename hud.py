# hud.py
import pygame
import math
from settings import (
    WIN_W,
    BOARD_X,
    BOARD_Y,
    BOARD_SIZE,
    PLAY_X,
    PLAY_Y,
    PLAY_SIZE,
    CENTER_X,
    CENTER_Y,
    STRIKER_R,
    PANEL_BG,
    CARD_BG,
    CARD_ACTIVE,
    BORDER_SUBTLE,
    CHESS_GREEN,
    CHESS_GREEN_DARK,
    CHESS_GREEN_LIGHT,
    GOLD,
    IVORY,
    CHARCOAL,
    QUEEN_RED,
    CREAM_TEXT,
    MUTED_TEXT,
)
from text_helper import load_font, render_candy_text


class ScoreboardHUD:
    def __init__(self):
        self.font_score = load_font(30, bold=True)
        self.font_md = load_font(15, bold=True)
        self.font_sm = load_font(12, bold=False)
        self.font_sm_bold = load_font(12, bold=True)

        # Pre-render the "Board Friends!" candy logo in Sodalicious style
        self.logo_surf = render_candy_text("Board Friends!", size=27)

    def _draw_text(self, screen, text, font, color, x, y, align="left", max_width=None):
        s_text = str(text)
        surf = font.render(s_text, True, color)
        if max_width and surf.get_width() > max_width:
            while len(s_text) > 4 and surf.get_width() > max_width:
                s_text = s_text[:-2] + "…"
                surf = font.render(s_text, True, color)

        rect = surf.get_rect()
        if align == "center":
            rect.centerx = int(x)
            rect.top = int(y)
        elif align == "right":
            rect.right = int(x)
            rect.top = int(y)
        elif align == "midcenter":
            rect.center = (int(x), int(y))
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

    def _draw_mini_coin_tray(self, screen, x, y, count_sunk, total_slots, coin_color, rim_color):
        slot_r = 6
        spacing = 16
        for i in range(total_slots):
            cx = x + i * spacing + slot_r
            cy = y + slot_r
            if i < count_sunk:
                pygame.draw.circle(screen, coin_color, (cx, cy), slot_r)
                pygame.draw.circle(screen, rim_color, (cx, cy), slot_r, 1)
            else:
                pygame.draw.circle(screen, (20, 19, 17), (cx, cy), slot_r)
                pygame.draw.circle(screen, (52, 49, 45), (cx, cy), slot_r, 1)

    def draw_aim_guide(self, screen, striker, coins, aim_xy):
        mx, my = aim_xy
        dx = striker.x - mx
        dy = striker.y - my
        pull_dist = math.hypot(dx, dy)

        if pull_dist < 6:
            return

        power_pct = min(1.0, pull_dist / 200.0)
        ux = dx / pull_dist
        uy = dy / pull_dist

        ring_r = int(STRIKER_R + 6 + 16 * power_pct)
        ring_col = (
            int(129 + 110 * power_pct),
            int(182 - 80 * power_pct),
            76,
        )
        ring_s = pygame.Surface((ring_r * 2 + 6, ring_r * 2 + 6), pygame.SRCALPHA)
        pygame.draw.circle(ring_s, (*ring_col, 150), (ring_r + 3, ring_r + 3), ring_r, 2)
        screen.blit(ring_s, (int(striker.x - ring_r - 3), int(striker.y - ring_r - 3)))

        pygame.draw.aaline(screen, (215, 208, 195), (striker.x, striker.y), (mx, my))
        pygame.draw.circle(screen, ring_col, (int(round(mx)), int(round(my))), 6)
        pygame.draw.circle(screen, IVORY, (int(round(mx)), int(round(my))), 3)

        ray_max = 520 * power_pct + 50
        hit_dist = ray_max
        target_coin = None

        min_x = PLAY_X + STRIKER_R
        max_x = PLAY_X + PLAY_SIZE - STRIKER_R
        min_y = PLAY_Y + STRIKER_R
        max_y = PLAY_Y + PLAY_SIZE - STRIKER_R

        if ux < -1e-5:
            hit_dist = min(hit_dist, (min_x - striker.x) / ux)
        elif ux > 1e-5:
            hit_dist = min(hit_dist, (max_x - striker.x) / ux)
        if uy < -1e-5:
            hit_dist = min(hit_dist, (min_y - striker.y) / uy)
        elif uy > 1e-5:
            hit_dist = min(hit_dist, (max_y - striker.y) / uy)

        for c in coins:
            if c.falling_in:
                continue
            fx = c.x - striker.x
            fy = c.y - striker.y
            proj = fx * ux + fy * uy
            if proj > 0:
                perp_sq = (fx * fx + fy * fy) - proj * proj
                touch_r = STRIKER_R + c.radius
                if perp_sq < touch_r * touch_r:
                    t = proj - math.sqrt(touch_r * touch_r - perp_sq)
                    if 0 < t < hit_dist:
                        hit_dist = t
                        target_coin = c

        end_x = striker.x + ux * hit_dist
        end_y = striker.y + uy * hit_dist
        pygame.draw.aaline(screen, (245, 232, 190), (striker.x, striker.y), (end_x, end_y))

        steps = int(hit_dist // 24)
        for i in range(1, steps + 1):
            px = int(round(striker.x + ux * (i * 24)))
            py = int(round(striker.y + uy * (i * 24)))
            pygame.draw.circle(screen, GOLD, (px, py), 2)

        if target_coin:
            gx = striker.x + ux * hit_dist
            gy = striker.y + uy * hit_dist
            ghost = pygame.Surface((STRIKER_R * 2 + 4, STRIKER_R * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                ghost, (255, 255, 255, 130), (STRIKER_R + 2, STRIKER_R + 2), STRIKER_R, 2
            )
            screen.blit(ghost, (int(round(gx - STRIKER_R - 2)), int(round(gy - STRIKER_R - 2))))

            nx = target_coin.x - gx
            ny = target_coin.y - gy
            nd = math.hypot(nx, ny)
            if nd > 0:
                nx /= nd
                ny /= nd
                deflect_x = target_coin.x + nx * (110 * power_pct + 24)
                deflect_y = target_coin.y + ny * (110 * power_pct + 24)
                pygame.draw.aaline(screen, GOLD, (target_coin.x, target_coin.y), (deflect_x, deflect_y))
                pygame.draw.circle(screen, GOLD, (int(round(deflect_x)), int(round(deflect_y))), 4)

    def draw_sidebar(self, screen, match, aim_xy):
        px = BOARD_X + BOARD_SIZE + 22
        pw = WIN_W - px - 22
        pcx = px + pw // 2

        # Chess.com Dark Slate Sidebar Container (#262421)
        pygame.draw.rect(screen, PANEL_BG, (px, BOARD_Y, pw, BOARD_SIZE), border_radius=14)
        pygame.draw.rect(screen, BORDER_SUBTLE, (px, BOARD_Y, pw, BOARD_SIZE), 2, border_radius=14)

        # Top Header Card with Sodalicious-style "Board Friends!" Title
        hx, hy, hw, hh = px + 14, BOARD_Y + 14, pw - 28, 72
        pygame.draw.rect(screen, CARD_BG, (hx, hy, hw, hh), border_radius=10)
        pygame.draw.rect(screen, CHESS_GREEN_DARK, (hx, hy + hh - 4, hw, 4), border_radius=2)
        pygame.draw.rect(screen, BORDER_SUBTLE, (hx, hy, hw, hh), 1, border_radius=10)

        logo_rect = self.logo_surf.get_rect(center=(pcx, hy + 34))
        screen.blit(self.logo_surf, logo_rect)

        white_on_board = sum(1 for c in match.coins if c.kind == "white" and not c.falling_in)
        black_on_board = sum(1 for c in match.coins if c.kind == "black" and not c.falling_in)
        white_sunk = max(0, 9 - white_on_board)
        black_sunk = max(0, 9 - black_on_board)

        players = [
            ("White (South)", IVORY, (180, 170, 155), match.scores[0], white_sunk, match.turn == 0, BOARD_Y + 98),
            ("Black (North)", CHARCOAL, (95, 100, 110), match.scores[1], black_sunk, match.turn == 1, BOARD_Y + 236),
        ]

        for label, c_fill, c_rim, score, sunk, is_turn, cy in players:
            cw, ch = pw - 28, 126
            cx = px + 14

            bg = CARD_ACTIVE if is_turn else CARD_BG
            border = CHESS_GREEN if is_turn else BORDER_SUBTLE
            pygame.draw.rect(screen, bg, (cx, cy, cw, ch), border_radius=10)

            # Chess.com signature left green accent bar on active player
            if is_turn:
                pygame.draw.rect(screen, CHESS_GREEN, (cx, cy, 6, ch), border_radius=4)
            pygame.draw.rect(screen, border, (cx, cy, cw, ch), 2 if is_turn else 1, border_radius=10)

            # Avatar / Coin Emblem
            pygame.draw.circle(screen, c_fill, (cx + 26, cy + 26), 11)
            pygame.draw.circle(screen, CHESS_GREEN if is_turn else c_rim, (cx + 26, cy + 26), 11, 2)
            self._draw_text(screen, label, self.font_md, CREAM_TEXT, cx + 46, cy + 16, "left")

            if is_turn:
                # 3D Chess.com green pill badge
                pill_x, pill_y, pill_w, pill_h = cx + cw - 84, cy + 13, 72, 22
                pygame.draw.rect(screen, CHESS_GREEN_DARK, (pill_x, pill_y + 2, pill_w, pill_h), border_radius=6)
                pygame.draw.rect(screen, CHESS_GREEN, (pill_x, pill_y, pill_w, pill_h), border_radius=6)
                self._draw_text(screen, "YOUR TURN", self.font_sm_bold, (255, 255, 255), pill_x + pill_w // 2, pill_y + 11, "midcenter")

            self._draw_text(screen, "CAPTURED PIECES", self.font_sm, MUTED_TEXT, cx + 16, cy + 54, "left")
            self._draw_mini_coin_tray(screen, cx + 16, cy + 76, sunk, 9, c_fill, c_rim)

            self._draw_text(screen, "SCORE", self.font_sm, MUTED_TEXT, cx + cw - 16, cy + 54, "right")
            self._draw_text(
                screen, score, self.font_score, CHESS_GREEN_LIGHT if is_turn else CREAM_TEXT, cx + cw - 16, cy + 70, "right"
            )

            p_idx = 0 if "White" in label else 1
            if match.queen_covered_by == p_idx:
                pygame.draw.circle(screen, QUEEN_RED, (cx + 185, cy + 82), 7)
                pygame.draw.circle(screen, GOLD, (cx + 185, cy + 82), 3)

        # Red Queen Status Card
        qy = BOARD_Y + 376
        qw = pw - 28
        qx = px + 14
        pygame.draw.rect(screen, CARD_BG, (qx, qy, qw, 66), border_radius=10)
        pygame.draw.rect(screen, BORDER_SUBTLE, (qx, qy, qw, 66), 1, border_radius=10)

        pygame.draw.circle(screen, QUEEN_RED, (qx + 26, qy + 33), 13)
        pygame.draw.circle(screen, GOLD, (qx + 26, qy + 33), 9, 1)
        pygame.draw.circle(screen, GOLD, (qx + 26, qy + 33), 4)

        self._draw_text(screen, "RED QUEEN (+3 BONUS)", self.font_sm_bold, GOLD, qx + 48, qy + 13, "left")
        if match.queen_covered_by is not None:
            owner = "White" if match.queen_covered_by == 0 else "Black"
            q_msg, q_col = f"Covered by {owner}", CHESS_GREEN_LIGHT
        elif match.queen_pending_for is not None:
            holder = "White" if match.queen_pending_for == 0 else "Black"
            q_msg, q_col = f"{holder} must sink a coin to cover!", (255, 120, 110)
        else:
            q_msg, q_col = "On the Board", CREAM_TEXT
        self._draw_text(screen, q_msg, self.font_sm, q_col, qx + 48, qy + 35, "left", max_width=qw - 60)

        # Strike Tension & Match Log Card
        gy = BOARD_Y + 454
        pygame.draw.rect(screen, CARD_BG, (qx, gy, qw, 90), border_radius=10)
        pygame.draw.rect(screen, BORDER_SUBTLE, (qx, gy, qw, 90), 1, border_radius=10)

        pull = math.hypot(match.striker.x - aim_xy[0], match.striker.y - aim_xy[1]) if match.phase == "AIM" else 0.0
        ratio = min(1.0, pull / 200.0)
        pct = int(round(ratio * 100))

        self._draw_text(screen, "SHOT POWER", self.font_sm_bold, MUTED_TEXT, qx + 14, gy + 12, "left")
        self._draw_text(screen, f"{pct}%", self.font_sm_bold, CHESS_GREEN_LIGHT if pct > 0 else MUTED_TEXT, qx + qw - 14, gy + 12, "right")

        bx, by, bw, bh = qx + 14, gy + 34, qw - 28, 14
        pygame.draw.rect(screen, (20, 19, 17), (bx, by, bw, bh), border_radius=7)
        if ratio > 0:
            fw = max(6, int(bw * ratio))
            pygame.draw.rect(screen, CHESS_GREEN, (bx, by, fw, bh), border_radius=7)
        pygame.draw.rect(screen, BORDER_SUBTLE, (bx, by, bw, bh), 1, border_radius=7)

        # Truncate log cleanly so it never overflows the right border
        self._draw_text(
            screen, match.last_note, self.font_sm, CREAM_TEXT, qx + 14, gy + 60, "left", max_width=qw - 28
        )

        # Controls Card
        ky = BOARD_Y + 556
        kh = 114
        pygame.draw.rect(screen, CARD_BG, (qx, ky, qw, kh), border_radius=10)
        pygame.draw.rect(screen, BORDER_SUBTLE, (qx, ky, qw, kh), 1, border_radius=10)

        tips = [
            ("Mouse", "Slide along baseline"),
            ("Left Click", "Lock pos / Release"),
            ("Right Click", "Cancel aim & re-place"),
            ("R Key", "New game"),
        ]
        for idx, (key_lbl, desc) in enumerate(tips):
            ry = ky + 12 + idx * 24
            kp_w = 82
            pygame.draw.rect(screen, (42, 40, 37), (qx + 12, ry, kp_w, 19), border_radius=5)
            pygame.draw.rect(screen, (68, 64, 58), (qx + 12, ry, kp_w, 19), 1, border_radius=5)
            self._draw_text(screen, key_lbl, self.font_sm_bold, CHESS_GREEN_LIGHT, qx + 12 + kp_w // 2, ry + 9, "midcenter")
            self._draw_text(screen, desc, self.font_sm, MUTED_TEXT, qx + 102, ry + 9, "midleft", max_width=qw - 112)

        # Chess.com Style 3D Green Action Button at Bottom
        fy = BOARD_Y + BOARD_SIZE - 54
        btn_h = 40
        pygame.draw.rect(screen, CHESS_GREEN_DARK, (qx, fy + 4, qw, btn_h), border_radius=8)
        pygame.draw.rect(screen, CHESS_GREEN, (qx, fy, qw, btn_h), border_radius=8)

        prompts = {
            "PLACE": "SLIDE & CLICK TO LOCK",
            "AIM": "PULL BACK & RELEASE!",
            "ROLLING": "SHOT IN PROGRESS...",
            "OVER": "PLAY AGAIN (PRESS R)",
        }
        self._draw_text(screen, prompts[match.phase], self.font_md, (255, 255, 255), pcx, fy + btn_h // 2, "midcenter")

    def draw_winner_modal(self, screen, headline):
        mw, mh = BOARD_SIZE - 90, 170
        mx = BOARD_X + 45
        my = CENTER_Y - mh // 2

        modal = pygame.Surface((mw, mh), pygame.SRCALPHA)
        pygame.draw.rect(modal, (30, 28, 26, 245), (0, 0, mw, mh), border_radius=16)
        screen.blit(modal, (mx, my))
        pygame.draw.rect(screen, CHESS_GREEN, (mx, my, mw, mh), 3, border_radius=16)

        candy_banner = render_candy_text(headline, size=34)
        screen.blit(candy_banner, candy_banner.get_rect(center=(CENTER_X, CENTER_Y - 22)))

        # Chess.com style green button inside modal
        btn_w, btn_h = 240, 38
        bx, by = CENTER_X - btn_w // 2, CENTER_Y + 24
        pygame.draw.rect(screen, CHESS_GREEN_DARK, (bx, by + 3, btn_w, btn_h), border_radius=8)
        pygame.draw.rect(screen, CHESS_GREEN, (bx, by, btn_w, btn_h), border_radius=8)
        self._draw_text(
            screen, "Press 'R' for Rematch", self.font_md, (255, 255, 255), CENTER_X, by + btn_h // 2, "midcenter"
        )
