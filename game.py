# game.py
import pygame
import math
import random
import sys

from config import (
    WIDTH,
    HEIGHT,
    FPS,
    PHYSICS_SUBSTEPS,
    PLAY_X,
    PLAY_Y,
    PLAY_SIZE,
    CENTER_X,
    CENTER_Y,
    BG_COLOR,
    WOOD_SURFACE,
    WHITE_COIN,
    BLACK_COIN,
    QUEEN_COIN,
    STRIKER_COLOR,
    GOLD,
    RED_ACCENT,
    FRICTION,
    RESTITUTION_COIN,
    RESTITUTION_WALL,
    MIN_VELOCITY,
    MAX_POWER,
    COIN_RADIUS,
    STRIKER_RADIUS,
    POCKET_RADIUS,
)
from entities import Disc
from effects import Particle, FloatingText, Shockwave
from board import CarromBoard
from ui import GameUI


class CarromGame:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Carrom Master - 2D Physics Edition")
        self.clock = pygame.time.Clock()

        self.board = CarromBoard()
        self.ui = GameUI()

        self.reset_game()

    def reset_game(self):
        self.coins = []
        self.particles = []
        self.shockwaves = []
        self.float_texts = []
        self.screen_shake = 0

        # Center Red Queen
        self.coins.append(Disc(CENTER_X, CENTER_Y, COIN_RADIUS, 1.0, QUEEN_COIN, "queen"))

        # Inner Ring (6 coins)
        r1 = COIN_RADIUS * 2.08
        for i in range(6):
            angle = i * (math.pi / 3) - math.pi / 2
            cx = CENTER_X + math.cos(angle) * r1
            cy = CENTER_Y + math.sin(angle) * r1
            ctype = "white" if i % 2 == 0 else "black"
            color = WHITE_COIN if ctype == "white" else BLACK_COIN
            self.coins.append(Disc(cx, cy, COIN_RADIUS, 1.0, color, ctype))

        # Outer Ring (12 coins)
        r2 = COIN_RADIUS * 4.15
        for i in range(12):
            angle = i * (math.pi / 6) - math.pi / 2
            cx = CENTER_X + math.cos(angle) * r2
            cy = CENTER_Y + math.sin(angle) * r2
            ctype = "white" if i % 2 == 0 else "black"
            color = WHITE_COIN if ctype == "white" else BLACK_COIN
            self.coins.append(Disc(cx, cy, COIN_RADIUS, 1.0, color, ctype))

        self.turn = 0  # 0 = White (Bottom), 1 = Black (Top)
        self.scores = [0, 0]
        self.queen_holder = None
        self.queen_covered_by = None

        self.striker = Disc(CENTER_X, 0, STRIKER_RADIUS, 1.85, STRIKER_COLOR, "striker")
        self.state = "PLACE_STRIKER"
        self.pocketed_this_turn = []
        self.winner_text = ""

        # Smooth aiming & placement interpolation coordinates
        self.aim_pos = [float(CENTER_X), float(CENTER_Y)]
        self.striker_target_x = float(CENTER_X)

        self.setup_striker_for_turn()

    def setup_striker_for_turn(self):
        span = PLAY_SIZE // 2 - 115
        self.striker_min_x = CENTER_X - span
        self.striker_max_x = CENTER_X + span
        self.striker.y = self.board.get_baseline_y(self.turn)
        self.striker.x = float(CENTER_X)
        self.striker_target_x = float(CENTER_X)
        self.striker.vx = 0.0
        self.striker.vy = 0.0
        self.striker.scale = 1.0
        self.striker.pocketing = False
        self.striker.trail.clear()

        # Avoid overlapping coins on the baseline
        if not self.is_striker_pos_valid(self.striker.x, self.striker.y):
            for offset in range(10, int(span), 8):
                if self.is_striker_pos_valid(CENTER_X + offset, self.striker.y):
                    self.striker.x = float(CENTER_X + offset)
                    self.striker_target_x = self.striker.x
                    break
                if self.is_striker_pos_valid(CENTER_X - offset, self.striker.y):
                    self.striker.x = float(CENTER_X - offset)
                    self.striker_target_x = self.striker.x
                    break

        self.state = "PLACE_STRIKER"
        self.pocketed_this_turn = []

    def is_striker_pos_valid(self, x, y):
        for c in self.coins:
            if not c.pocketing and math.hypot(c.x - x, c.y - y) < (STRIKER_RADIUS + c.radius + 2):
                return False
        return True

    def spawn_coin_near_center(self, disc_type):
        color = (
            WHITE_COIN
            if disc_type == "white"
            else (BLACK_COIN if disc_type == "black" else QUEEN_COIN)
        )
        for dist in range(0, 220, 6):
            for deg in range(0, 360, 20):
                rad = math.radians(deg)
                tx = CENTER_X + math.cos(rad) * dist
                ty = CENTER_Y + math.sin(rad) * dist
                if all(
                    math.hypot(c.x - tx, c.y - ty) >= COIN_RADIUS * 2 + 2
                    for c in self.coins
                    if not c.pocketing
                ):
                    new_coin = Disc(tx, ty, COIN_RADIUS, 1.0, color, disc_type)
                    self.coins.append(new_coin)
                    self.shockwaves.append(Shockwave(tx, ty, GOLD, 42))
                    return

    # ------------------------------------------------------------------------
    # PHYSICS & COLLISIONS
    # ------------------------------------------------------------------------
    def update_physics(self):
        all_discs = self.coins + (
            [self.striker] if not self.striker.pocketing or self.striker.scale > 0 else []
        )

        # Animate pocketing discs shrinking into the pocket
        for d in list(all_discs):
            if d.pocketing:
                px, py = d.pocket_target
                d.x += (px - d.x) * 0.28
                d.y += (py - d.y) * 0.28
                d.scale -= 0.09
                if d.scale <= 0.05:
                    if d in self.coins:
                        self.coins.remove(d)
                    d.scale = 0.0
                    # Crucial fix: clear pocketing flag on Striker so is_moving becomes False!
                    d.pocketing = False

        active_discs = [d for d in self.coins if not d.pocketing]
        if not self.striker.pocketing and self.striker.scale > 0:
            active_discs.append(self.striker)

        # Sub-stepped integration and collision resolution
        for _ in range(PHYSICS_SUBSTEPS):
            for d in active_discs:
                d.x += d.vx / PHYSICS_SUBSTEPS
                d.y += d.vy / PHYSICS_SUBSTEPS

            # Wall Collisions
            min_x, max_x = PLAY_X, PLAY_X + PLAY_SIZE
            min_y, max_y = PLAY_Y, PLAY_Y + PLAY_SIZE

            for d in active_discs:
                hit_wall = False
                if d.x - d.radius < min_x:
                    d.x = min_x + d.radius
                    d.vx = abs(d.vx) * RESTITUTION_WALL
                    hit_wall = True
                elif d.x + d.radius > max_x:
                    d.x = max_x - d.radius
                    d.vx = -abs(d.vx) * RESTITUTION_WALL
                    hit_wall = True

                if d.y - d.radius < min_y:
                    d.y = min_y + d.radius
                    d.vy = abs(d.vy) * RESTITUTION_WALL
                    hit_wall = True
                elif d.y + d.radius > max_y:
                    d.y = max_y - d.radius
                    d.vy = -abs(d.vy) * RESTITUTION_WALL
                    hit_wall = True

                if hit_wall and d.speed > 5.0:
                    for _ in range(3):
                        self.particles.append(Particle(d.x, d.y, WOOD_SURFACE, 0.5, 2.5, 3, 15))

            # Disc-to-Disc Elastic Collisions
            n = len(active_discs)
            for i in range(n):
                for j in range(i + 1, n):
                    d1, d2 = active_discs[i], active_discs[j]
                    dx = d2.x - d1.x
                    dy = d2.y - d1.y
                    dist = math.hypot(dx, dy)
                    min_dist = d1.radius + d2.radius

                    if 0 < dist < min_dist:
                        nx, ny = dx / dist, dy / dist
                        overlap = min_dist - dist
                        total_mass = d1.mass + d2.mass

                        d1.x -= nx * overlap * (d2.mass / total_mass)
                        d1.y -= ny * overlap * (d2.mass / total_mass)
                        d2.x += nx * overlap * (d1.mass / total_mass)
                        d2.y += ny * overlap * (d1.mass / total_mass)

                        rvx = d2.vx - d1.vx
                        rvy = d2.vy - d1.vy
                        vel_along_normal = rvx * nx + rvy * ny

                        if vel_along_normal < 0:
                            j_impulse = -(1 + RESTITUTION_COIN) * vel_along_normal
                            j_impulse /= 1 / d1.mass + 1 / d2.mass

                            impulse_x = j_impulse * nx
                            impulse_y = j_impulse * ny

                            d1.vx -= impulse_x / d1.mass
                            d1.vy -= impulse_y / d1.mass
                            d2.vx += impulse_x / d2.mass
                            d2.vy += impulse_y / d2.mass

                            impact = abs(vel_along_normal)
                            if impact > 3.5:
                                mid_x = (d1.x + d2.x) / 2
                                mid_y = (d1.y + d2.y) / 2
                                for _ in range(min(14, int(impact * 1.2))):
                                    self.particles.append(
                                        Particle(mid_x, mid_y, GOLD, 1.0, impact * 0.4, 3, 20)
                                    )
                                if impact > 11.0:
                                    self.screen_shake = min(10, int(impact * 0.45))
                                    self.shockwaves.append(Shockwave(mid_x, mid_y, WHITE_COIN, 32))

        # Friction & Pocket Detection
        for d in active_discs:
            d.vx *= FRICTION
            d.vy *= FRICTION
            if d.speed < MIN_VELOCITY:
                d.vx = 0.0
                d.vy = 0.0
            d.update_trail()

            for px, py in self.board.pockets:
                if math.hypot(d.x - px, d.y - py) < POCKET_RADIUS - 3:
                    d.pocketing = True
                    d.pocket_target = (px, py)
                    d.vx = 0.0
                    d.vy = 0.0
                    self.pocketed_this_turn.append(d.disc_type)
                    self.trigger_pocket_effect(px, py, d)
                    break

        if not (any(c.is_moving for c in self.coins) or self.striker.is_moving):
            self.evaluate_turn_end()

    def trigger_pocket_effect(self, px, py, disc):
        self.shockwaves.append(Shockwave(px, py, disc.color, 52))
        for _ in range(25):
            self.particles.append(Particle(px, py, disc.color, 2, 8, 5, 35))

        if disc.disc_type == "striker":
            self.screen_shake = 10
            self.float_texts.append(FloatingText(px, py, "STRIKER FOUL! -1", RED_ACCENT, 22))
        elif disc.disc_type == "queen":
            self.screen_shake = 8
            self.float_texts.append(FloatingText(px, py, "QUEEN!", QUEEN_COIN, 24))
        else:
            label = "WHITE +1" if disc.disc_type == "white" else "BLACK +1"
            is_own = (self.turn == 0 and disc.disc_type == "white") or (
                self.turn == 1 and disc.disc_type == "black"
            )
            col = GOLD if is_own else (180, 180, 195)
            self.float_texts.append(FloatingText(px, py, label, col, 20))

    # ------------------------------------------------------------------------
    # TURN RULES & SCORING
    # ------------------------------------------------------------------------
    def evaluate_turn_end(self):
        my_type = "white" if self.turn == 0 else "black"
        opp_type = "black" if self.turn == 0 else "white"

        foul = "striker" in self.pocketed_this_turn
        my_pocketed = self.pocketed_this_turn.count(my_type)
        opp_pocketed = self.pocketed_this_turn.count(opp_type)
        queen_pocketed = "queen" in self.pocketed_this_turn

        self.scores[self.turn] += my_pocketed
        self.scores[1 - self.turn] += opp_pocketed

        keep_turn = False

        # Check pending Queen Cover
        if self.queen_holder == self.turn:
            if my_pocketed > 0 and not foul:
                self.queen_covered_by = self.turn
                self.queen_holder = None
                self.scores[self.turn] += 3
                self.float_texts.append(
                    FloatingText(CENTER_X, CENTER_Y, "QUEEN COVERED! +3", GOLD, 26)
                )
                keep_turn = True
            else:
                self.queen_holder = None
                self.spawn_coin_near_center("queen")
                self.float_texts.append(
                    FloatingText(CENTER_X, CENTER_Y, "QUEEN RETURNED", QUEEN_COIN, 22)
                )

        # Check Queen pocketed on this shot
        if queen_pocketed:
            if foul:
                self.spawn_coin_near_center("queen")
                self.float_texts.append(
                    FloatingText(CENTER_X, CENTER_Y, "FOUL! QUEEN RETURNED", RED_ACCENT, 22)
                )
            elif my_pocketed > 0:
                self.queen_covered_by = self.turn
                self.scores[self.turn] += 3
                self.float_texts.append(
                    FloatingText(CENTER_X, CENTER_Y, "QUEEN COVERED! +3", GOLD, 26)
                )
                keep_turn = True
            else:
                self.queen_holder = self.turn
                self.float_texts.append(
                    FloatingText(CENTER_X, CENTER_Y, "COVER THE QUEEN!", GOLD, 24)
                )
                keep_turn = True

        if my_pocketed > 0 and not foul:
            keep_turn = True

        # Striker Foul Penalty: Deduct 1 point, return player's coin to center, pass turn
        if foul:
            keep_turn = False
            self.scores[self.turn] -= 1
            my_coins_on_board = sum(1 for c in self.coins if c.disc_type == my_type)
            if my_coins_on_board < 9:
                self.spawn_coin_near_center(my_type)
                self.float_texts.append(
                    FloatingText(CENTER_X, CENTER_Y + 28, f"{my_type.upper()} COIN RETURNED", RED_ACCENT, 20)
                )

        # Check Match Over
        white_left = sum(1 for c in self.coins if c.disc_type == "white")
        black_left = sum(1 for c in self.coins if c.disc_type == "black")
        queen_on_board = (
            any(c.disc_type == "queen" for c in self.coins) or self.queen_holder is not None
        )

        if (white_left == 0 or black_left == 0) and not queen_on_board:
            self.state = "GAME_OVER"
            if self.scores[0] > self.scores[1]:
                self.winner_text = "PLAYER 1 (WHITE) WINS!"
            elif self.scores[1] > self.scores[0]:
                self.winner_text = "PLAYER 2 (BLACK) WINS!"
            else:
                self.winner_text = "IT'S A DRAW!"
            return

        if not keep_turn:
            self.turn = 1 - self.turn

        self.setup_striker_for_turn()

    # ------------------------------------------------------------------------
    # EVENT HANDLING & MAIN LOOP
    # ------------------------------------------------------------------------
    def handle_events(self, mouse_pos):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset_game()

            if self.state == "PLACE_STRIKER":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.is_striker_pos_valid(self.striker.x, self.striker.y):
                        self.state = "AIMING"
                        self.aim_pos = [float(mouse_pos[0]), float(mouse_pos[1])]

            elif self.state == "AIMING":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    self.state = "PLACE_STRIKER"
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    dx = self.striker.x - self.aim_pos[0]
                    dy = self.striker.y - self.aim_pos[1]
                    dist = math.hypot(dx, dy)
                    if dist > 10:
                        power = min(MAX_POWER, (dist / 200.0) * MAX_POWER)
                        self.striker.vx = (dx / dist) * power
                        self.striker.vy = (dy / dist) * power
                        self.state = "SIMULATING"
                    else:
                        self.state = "PLACE_STRIKER"

    def update_smooth_controls(self, mouse_pos):
        if self.state == "PLACE_STRIKER":
            clamped_x = max(self.striker_min_x, min(self.striker_max_x, float(mouse_pos[0])))
            if self.is_striker_pos_valid(clamped_x, self.striker.y):
                self.striker_target_x = clamped_x
            # Smoothly interpolate striker along baseline
            next_x = self.striker.x + (self.striker_target_x - self.striker.x) * 0.45
            if self.is_striker_pos_valid(next_x, self.striker.y):
                self.striker.x = next_x

        elif self.state == "AIMING":
            # Exponential smoothing (lerp) eliminates mouse jitter
            self.aim_pos[0] += (mouse_pos[0] - self.aim_pos[0]) * 0.35
            self.aim_pos[1] += (mouse_pos[1] - self.aim_pos[1]) * 0.35

    def run(self):
        while True:
            mouse_pos = pygame.mouse.get_pos()
            self.handle_events(mouse_pos)
            self.update_smooth_controls(mouse_pos)

            if self.state == "SIMULATING":
                self.update_physics()

            # Update Visual Effects
            for effect_list in (self.particles, self.shockwaves, self.float_texts):
                for item in list(effect_list):
                    item.update()
                    if item.life <= 0:
                        effect_list.remove(item)

            shake_offset = (0, 0)
            if self.screen_shake > 0:
                shake_offset = (
                    random.randint(-self.screen_shake, self.screen_shake),
                    random.randint(-self.screen_shake, self.screen_shake),
                )
                self.screen_shake = max(0, self.screen_shake - 1)

            # Render Frame
            self.screen.fill(BG_COLOR)
            self.board.draw(self.screen, shake_offset)

            if self.state == "PLACE_STRIKER":
                self.board.draw_active_baseline(
                    self.screen, self.turn, self.striker_min_x, self.striker_max_x, shake_offset
                )

            for sw in self.shockwaves:
                sw.draw(self.screen)

            for c in self.coins:
                c.draw(self.screen, shake_offset)

            if self.striker.scale > 0:
                self.striker.draw(self.screen, shake_offset)

            if self.state == "AIMING":
                self.ui.draw_aim_guide(self.screen, self.striker, self.coins, self.aim_pos)

            for p in self.particles:
                p.draw(self.screen)
            for ft in self.float_texts:
                ft.draw(self.screen)

            self.ui.draw_hud(self.screen, self, self.aim_pos)

            if self.state == "GAME_OVER":
                self.ui.draw_game_over(self.screen, self.winner_text)

            pygame.display.flip()
            self.clock.tick(FPS)
