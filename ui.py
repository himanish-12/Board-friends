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
)


class GameUI:
    def __init__(self):
        self.font_lg = pygame.font.SysFont("Segoe UI", 30, bold=True)
        self.font_md = pygame.font.SysFont("Segoe UI", 20, bold=True)
        self.font_sm = pygame.font.SysFont("Segoe UI", 15)

    def draw_aim_guide(self, screen, striker, coins, mouse_pos):
        mx, my = mouse_pos
        dx = striker.x - mx
        dy = striker.y - my
        dist = math.hypot(dx, dy)

        if dist < 8:
            return

        power_ratio = min(1.0, dist / 200.0)
        ux = dx / dist
        uy = dy / dist

        # Elastic pullback line
        pygame.draw.line(screen, (255, 255, 255), (int(striker.x), int(striker.y)), (mx, my), 2)
        pygame.draw.circle(screen, GOLD, (mx, my), 6)

        # Raycast forward to find first coin collision
        ray_len = 480 * power_ratio + 60
        closest_t = ray_len
        hit_coin = None

        for c in coins:
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

        # Dotted trajectory line
        steps = int(closest_t // 16)
        for i in range(1, steps + 1):
            px = int(striker.x + ux * (i * 16))
            py = int(striker.y + uy * (i * 16))
            if PLAY_X < px < PLAY_X + PLAY_SIZE and PLAY_Y < py < PLAY_Y + PLAY_SIZE:
                pygame.draw.circle(screen, (255, 245, 200), (px, py), 3)

        # Ghost striker & deflection vector at impact
        if hit_coin:
            gx = striker.x + ux * closest_t
            gy = striker.y + uy * closest_t
            ghost_s = pygame.Surface((STRIKER_RADIUS * 2 + 4, STRIKER_RADIUS * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(
                ghost_s, (255, 255, 255, 110), (STRIKER_RADIUS + 2, STRIKER_RADIUS + 2), STRIKER_RADIUS, 2
            )
            screen.blit(ghost_s, (int(gx - STRIKER_RADIUS - 2), int(gy - STRIKER_RADIUS - 2)))

            nx = hit_coin.x - gx
            ny = hit_coin.y - gy
            nd = math.hypot(nx, ny)
            if nd > 0:
                nx /= nd
                ny /= nd
                end_x = int(hit_coin.x + nx * 95 * power_ratio)
                end_y = int(hit_coin.y + ny * 95 * power_ratio)
                pygame.draw.line(screen, GOLD, (int(hit_coin.x), int(hit_coin.y)), (end_x, end_y), 3)
                pygame.draw.circle(screen, GOLD, (end_x, end_y), 4)

    def draw_hud(self, screen, game, mouse_pos):
        panel_x = BOARD_X + BOARD_SIZE + 25
        panel_w = WIDTH - panel_x - 25

        # Sidebar Card Background
        pygame.draw.rect(screen, (32, 35, 44), (panel_x, BOARD_Y, panel_w, BOARD_SIZE), border_radius=16)
        pygame.draw.rect(screen, (55, 60, 75), (panel_x, BOARD_Y, panel_w, BOARD_SIZE), 2, border_radius=16)

        # Title
        title = self.font_lg.render("CARROM", True, GOLD)
        screen.blit(title, (panel_x + 22, BOARD_Y + 20))
        sub = self.font_sm.render("PHYSICS EDITION", True, (160, 165, 180))
        screen.blit(sub, (panel_x + 24, BOARD_Y + 55))

        # Player Score Cards
        players = [
            ("Player 1 (White)", WHITE_COIN, game.scores[0], game.turn == 0, BOARD_Y + 105),
            ("Player 2 (Black)", BLACK_COIN, game.scores[1], game.turn == 1, BOARD_Y + 230),
        ]

        for name, col, score, active, py in players:
            bg_col = (48, 54, 68) if active else (26, 28, 36)
            border_col = GOLD if active else (45, 48, 58)
            pygame.draw.rect(screen, bg_col, (panel_x + 15, py, panel_w - 30, 105), border_radius=12)
            pygame.draw.rect(screen, border_col, (panel_x + 15, py, panel_w - 30, 105), 2, border_radius=12)

            pygame.draw.circle(screen, col, (panel_x + 38, py + 30), 12)
            pygame.draw.circle(screen, (120, 120, 120), (panel_x + 38, py + 30), 12, 1)

            lbl = self.font_md.render(name, True, (240, 240, 245))
            screen.blit(lbl, (panel_x + 58, py + 17))

            sc_lbl = self.font_lg.render(f"Score: {score}", True, GOLD if active else (185, 190, 205))
            screen.blit(sc_lbl, (panel_x + 30, py + 52))

        # Queen Status Box
        qy = BOARD_Y + 365
        pygame.draw.rect(screen, (26, 28, 36), (panel_x + 15, qy, panel_w - 30, 75), border_radius=10)
        q_title = self.font_sm.render("QUEEN STATUS (+3 PTS)", True, QUEEN_COIN)
        screen.blit(q_title, (panel_x + 28, qy + 12))

        if game.queen_covered_by is not None:
            q_status = f"Covered by Player {game.queen_covered_by + 1}"
            q_col = GOLD
        elif game.queen_holder is not None:
            q_status = f"P{game.queen_holder + 1}: Must Cover Now!"
            q_col = (255, 120, 120)
        else:
            q_status = "On the Board"
            q_col = (200, 205, 215)

        q_txt = self.font_md.render(q_status, True, q_col)
        screen.blit(q_txt, (panel_x + 28, qy + 36))

        # Shot Power Meter
        pmy = BOARD_Y + 465
        pm_lbl = self.font_sm.render("SHOT POWER", True, (180, 185, 200))
        screen.blit(pm_lbl, (panel_x + 20, pmy))

        pygame.draw.rect(screen, (20, 22, 28), (panel_x + 20, pmy + 25, panel_w - 40, 22), border_radius=8)
        if game.state == "AIMING":
            dist = math.hypot(game.striker.x - mouse_pos[0], game.striker.y - mouse_pos[1])
            ratio = min(1.0, dist / 200.0)
            fill_w = int((panel_w - 44) * ratio)
            bar_color = (int(60 + 195 * ratio), int(220 - 160 * ratio), 50)
            if fill_w > 0:
                pygame.draw.rect(screen, bar_color, (panel_x + 22, pmy + 27, fill_w, 18), border_radius=6)

        # Controls Guide
        cy = BOARD_Y + 535
        controls = [
            "CONTROLS:",
            "1. Move Mouse: Slide Striker",
            "2. Left Click: Lock Position",
            "3. Drag Back & Release: Shoot",
            "4. Right Click: Cancel Aim",
            "5. Press 'R': Reset Match",
        ]
        for i, line in enumerate(controls):
            col = GOLD if i == 0 else (165, 170, 185)
            txt = self.font_sm.render(line, True, col)
            screen.blit(txt, (panel_x + 20, cy + i * 26))

        # Current State Footer
        banner_y = BOARD_Y + BOARD_SIZE - 45
        state_str = {
            "PLACE_STRIKER": "Slide & Click to Place Striker",
            "AIMING": "Pull Back to Aim & Release!",
            "SIMULATING": "Shot in Progress...",
            "GAME_OVER": "Match Complete! Press R",
        }[game.state]
        st_render = self.font_sm.render(state_str, True, GOLD)
        screen.blit(st_render, (panel_x + 20, banner_y))

    def draw_game_over(self, screen, winner_text):
        overlay = pygame.Surface((BOARD_SIZE, 140), pygame.SRCALPHA)
        overlay.fill((15, 18, 24, 225))
        screen.blit(overlay, (BOARD_X, CENTER_Y - 70))
        win_surf = self.font_lg.render(winner_text, True, GOLD)
        sub_surf = self.font_md.render("Press 'R' to Play Again", True, WHITE_COIN)
        screen.blit(win_surf, win_surf.get_rect(center=(CENTER_X, CENTER_Y - 18)))
        screen.blit(sub_surf, sub_surf.get_rect(center=(CENTER_X, CENTER_Y + 25)))