# match.py
import pygame
import math
import random
import sys

from settings import (
    WIN_W,
    WIN_H,
    FPS,
    SUBSTEPS,
    PLAY_X,
    PLAY_Y,
    PLAY_SIZE,
    CENTER_X,
    CENTER_Y,
    BG_DARK,
    BOARD_WOOD,
    IVORY,
    CHARCOAL,
    QUEEN_RED,
    STRIKER_TEAL,
    GOLD,
    CRIMSON,
    BOARD_DRAG,
    COIN_BOUNCE,
    CUSHION_BOUNCE,
    STOP_SPEED,
    MAX_STRIKE_POWER,
    COIN_R,
    STRIKER_R,
    POCKET_R,
)
from pieces import CarromPiece
from fx import Spark, CalloutToast, Ripple
from board import CarromBoard
from hud import ScoreboardHUD


class CarromMatch:
    def __init__(self):
        pygame.display.init()
        self.screen = pygame.display.set_mode((WIN_W, WIN_H))
        pygame.display.set_caption("Board Friends")
        self.clock = pygame.time.Clock()

        self.board = CarromBoard()
        self.hud = ScoreboardHUD()

        # Fun Sodalicious-style callout words when pocketing coins
        self.sweet_words = ["Sodalicious!", "Juicy!", "Crush!", "Divine!", "Tasty!"]

        self.rack_new_game()

    def rack_new_game(self):
        self.coins = []
        self.sparks = []
        self.ripples = []
        self.toasts = []
        self.shake_frames = 0

        # Red Queen sits dead center
        self.coins.append(CarromPiece(CENTER_X, CENTER_Y, COIN_R, 1.0, QUEEN_RED, "queen"))

        # Inner ring of 6 alternating coins
        r_inner = COIN_R * 2.08
        for i in range(6):
            ang = i * (math.pi / 3) - math.pi / 2
            cx = CENTER_X + math.cos(ang) * r_inner
            cy = CENTER_Y + math.sin(ang) * r_inner
            kind = "white" if i % 2 == 0 else "black"
            col = IVORY if kind == "white" else CHARCOAL
            self.coins.append(CarromPiece(cx, cy, COIN_R, 1.0, col, kind))

        # Outer ring of 12 alternating coins
        r_outer = COIN_R * 4.15
        for i in range(12):
            ang = i * (math.pi / 6) - math.pi / 2
            cx = CENTER_X + math.cos(ang) * r_outer
            cy = CENTER_Y + math.sin(ang) * r_outer
            kind = "white" if i % 2 == 0 else "black"
            col = IVORY if kind == "white" else CHARCOAL
            self.coins.append(CarromPiece(cx, cy, COIN_R, 1.0, col, kind))

        self.turn = 0  # 0: White (South), 1: Black (North)
        self.scores = [0, 0]
        self.queen_pending_for = None
        self.queen_covered_by = None
        self.last_note = "New game started — White breaks!"

        self.striker = CarromPiece(CENTER_X, 0, STRIKER_R, 1.85, STRIKER_TEAL, "striker")
        self.phase = "PLACE"
        self.sunk_this_shot = []
        self.winner_banner = ""

        self.aim_xy = [float(CENTER_X), float(CENTER_Y)]
        self.target_striker_x = float(CENTER_X)

        self.toasts.append(CalloutToast(CENTER_X, CENTER_Y - 110, "Shuffling!", GOLD, 28))
        self.ready_striker_on_line()

    def ready_striker_on_line(self):
        span = PLAY_SIZE // 2 - 115
        self.lane_min_x = CENTER_X - span
        self.lane_max_x = CENTER_X + span
        self.striker.y = self.board.baseline_y_for(self.turn)
        self.striker.x = float(CENTER_X)
        self.target_striker_x = float(CENTER_X)
        self.striker.vx = 0.0
        self.striker.vy = 0.0
        self.striker.scale = 1.0
        self.striker.falling_in = False
        self.striker.trail.clear()

        if not self.spot_is_clear(self.striker.x, self.striker.y):
            for step in range(10, int(span), 8):
                if self.spot_is_clear(CENTER_X + step, self.striker.y):
                    self.striker.x = float(CENTER_X + step)
                    self.target_striker_x = self.striker.x
                    break
                if self.spot_is_clear(CENTER_X - step, self.striker.y):
                    self.striker.x = float(CENTER_X - step)
                    self.target_striker_x = self.striker.x
                    break

        self.phase = "PLACE"
        self.sunk_this_shot = []

    def spot_is_clear(self, x, y):
        for c in self.coins:
            if not c.falling_in and math.hypot(c.x - x, c.y - y) < (STRIKER_R + c.radius + 2):
                return False
        return True

    def return_coin_to_center(self, kind):
        col = IVORY if kind == "white" else (CHARCOAL if kind == "black" else QUEEN_RED)
        for dist in range(0, 220, 6):
            for deg in range(0, 360, 20):
                rad = math.radians(deg)
                tx = CENTER_X + math.cos(rad) * dist
                ty = CENTER_Y + math.sin(rad) * dist
                if all(
                    math.hypot(c.x - tx, c.y - ty) >= COIN_R * 2 + 2
                    for c in self.coins
                    if not c.falling_in
                ):
                    self.coins.append(CarromPiece(tx, ty, COIN_R, 1.0, col, kind))
                    self.ripples.append(Ripple(tx, ty, GOLD, 42))
                    return

    def step_physics(self):
        all_pieces = self.coins + (
            [self.striker] if not self.striker.falling_in or self.striker.scale > 0 else []
        )

        for p in list(all_pieces):
            if p.falling_in:
                px, py = p.pocket_xy
                p.x += (px - p.x) * 0.28
                p.y += (py - p.y) * 0.28
                p.scale -= 0.09
                if p.scale <= 0.05:
                    if p in self.coins:
                        self.coins.remove(p)
                    p.scale = 0.0
                    p.falling_in = False

        live = [c for c in self.coins if not c.falling_in]
        if not self.striker.falling_in and self.striker.scale > 0:
            live.append(self.striker)

        for _ in range(SUBSTEPS):
            for p in live:
                p.x += p.vx / SUBSTEPS
                p.y += p.vy / SUBSTEPS

            min_x, max_x = PLAY_X, PLAY_X + PLAY_SIZE
            min_y, max_y = PLAY_Y, PLAY_Y + PLAY_SIZE

            for p in live:
                bounced = False
                if p.x - p.radius < min_x:
                    p.x = min_x + p.radius
                    p.vx = abs(p.vx) * CUSHION_BOUNCE
                    bounced = True
                elif p.x + p.radius > max_x:
                    p.x = max_x - p.radius
                    p.vx = -abs(p.vx) * CUSHION_BOUNCE
                    bounced = True

                if p.y - p.radius < min_y:
                    p.y = min_y + p.radius
                    p.vy = abs(p.vy) * CUSHION_BOUNCE
                    bounced = True
                elif p.y + p.radius > max_y:
                    p.y = max_y - p.radius
                    p.vy = -abs(p.vy) * CUSHION_BOUNCE
                    bounced = True

                if bounced and p.speed > 5.0:
                    for _ in range(3):
                        self.sparks.append(Spark(p.x, p.y, BOARD_WOOD, 0.5, 2.5, 3, 14))

            count = len(live)
            for i in range(count):
                for j in range(i + 1, count):
                    a, b = live[i], live[j]
                    dx = b.x - a.x
                    dy = b.y - a.y
                    dist = math.hypot(dx, dy)
                    min_sep = a.radius + b.radius

                    if 0 < dist < min_sep:
                        nx, ny = dx / dist, dy / dist
                        overlap = min_sep - dist
                        m_sum = a.mass + b.mass

                        a.x -= nx * overlap * (b.mass / m_sum)
                        a.y -= ny * overlap * (b.mass / m_sum)
                        b.x += nx * overlap * (a.mass / m_sum)
                        b.y += ny * overlap * (a.mass / m_sum)

                        rvx = b.vx - a.vx
                        rvy = b.vy - a.vy
                        vn = rvx * nx + rvy * ny

                        if vn < 0:
                            impulse = -(1 + COIN_BOUNCE) * vn / (1 / a.mass + 1 / b.mass)
                            ix, iy = impulse * nx, impulse * ny

                            a.vx -= ix / a.mass
                            a.vy -= iy / a.mass
                            b.vx += ix / b.mass
                            b.vy += iy / b.mass

                            clack = abs(vn)
                            if clack > 3.5:
                                mx, my = (a.x + b.x) / 2, (a.y + b.y) / 2
                                for _ in range(min(12, int(clack * 1.1))):
                                    self.sparks.append(Spark(mx, my, GOLD, 1.0, clack * 0.38, 3, 18))
                                if clack > 11.5:
                                    self.shake_frames = min(9, int(clack * 0.42))
                                    self.ripples.append(Ripple(mx, my, IVORY, 30))

        for p in live:
            p.vx *= BOARD_DRAG
            p.vy *= BOARD_DRAG
            if p.speed < STOP_SPEED:
                p.vx = 0.0
                p.vy = 0.0
            p.record_trail()

            for px, py in self.board.pockets:
                if math.hypot(p.x - px, p.y - py) < POCKET_R - 3:
                    p.falling_in = True
                    p.pocket_xy = (px, py)
                    p.vx = 0.0
                    p.vy = 0.0
                    self.sunk_this_shot.append(p.kind)
                    self._on_piece_pocketed(px, py, p)
                    break

        if not (any(c.in_motion for c in self.coins) or self.striker.in_motion):
            self.score_shot_and_pass_turn()

    def _on_piece_pocketed(self, px, py, piece):
        self.ripples.append(Ripple(px, py, piece.color, 50))
        for _ in range(22):
            self.sparks.append(Spark(px, py, piece.color, 2, 7.5, 4, 32))

        # Clamp popup X/Y slightly toward board interior so big candy text stays fully on-board
        tx = max(PLAY_X + 95, min(PLAY_X + PLAY_SIZE - 95, px))
        ty = max(PLAY_Y + 45, min(PLAY_Y + PLAY_SIZE - 45, py))

        if piece.kind == "striker":
            self.shake_frames = 10
            self.toasts.append(CalloutToast(tx, ty, "Foul! -1", CRIMSON, 26))
        elif piece.kind == "queen":
            self.shake_frames = 8
            self.toasts.append(CalloutToast(tx, ty, "Divine!", GOLD, 30))
        else:
            word = random.choice(self.sweet_words)
            self.toasts.append(CalloutToast(tx, ty, word, GOLD, 26))

    def score_shot_and_pass_turn(self):
        my_coin = "white" if self.turn == 0 else "black"
        opp_coin = "black" if self.turn == 0 else "white"
        who = "White" if self.turn == 0 else "Black"

        fouled = "striker" in self.sunk_this_shot
        my_sunk = self.sunk_this_shot.count(my_coin)
        opp_sunk = self.sunk_this_shot.count(opp_coin)
        queen_sunk = "queen" in self.sunk_this_shot

        self.scores[self.turn] += my_sunk
        self.scores[1 - self.turn] += opp_sunk

        shoot_again = False
        self.last_note = f"{who} missed — turn passes."

        if self.queen_pending_for == self.turn:
            if my_sunk > 0 and not fouled:
                self.queen_covered_by = self.turn
                self.queen_pending_for = None
                self.scores[self.turn] += 3
                self.last_note = f"{who} covered Queen! (+3)"
                self.toasts.append(CalloutToast(CENTER_X, CENTER_Y, "Sodalicious! +3", GOLD, 32))
                shoot_again = True
            else:
                self.queen_pending_for = None
                self.return_coin_to_center("queen")
                self.last_note = "Queen returned to center."
                self.toasts.append(CalloutToast(CENTER_X, CENTER_Y, "Queen Returned!", QUEEN_RED, 24))

        if queen_sunk:
            if fouled:
                self.return_coin_to_center("queen")
                self.last_note = "Foul! Queen returned."
                self.toasts.append(CalloutToast(CENTER_X, CENTER_Y, "Queen Returned!", CRIMSON, 24))
            elif my_sunk > 0:
                self.queen_covered_by = self.turn
                self.scores[self.turn] += 3
                self.last_note = f"{who} covered Queen! (+3)"
                self.toasts.append(CalloutToast(CENTER_X, CENTER_Y, "Sodalicious! +3", GOLD, 32))
                shoot_again = True
            else:
                self.queen_pending_for = self.turn
                self.last_note = f"{who}: Sink a coin to cover!"
                self.toasts.append(CalloutToast(CENTER_X, CENTER_Y, "Cover Queen!", GOLD, 28))
                shoot_again = True

        if my_sunk > 0 and not fouled:
            shoot_again = True
            if not queen_sunk and self.queen_covered_by != self.turn:
                self.last_note = f"{who} scored +{my_sunk} — shoots again!"

        if fouled:
            shoot_again = False
            self.scores[self.turn] -= 1
            on_table = sum(1 for c in self.coins if c.kind == my_coin)
            if on_table < 9:
                self.return_coin_to_center(my_coin)
                self.last_note = f"{who} fouled! -1 & coin returned."
            else:
                self.last_note = f"{who} fouled! (-1 pt)"

        w_left = sum(1 for c in self.coins if c.kind == "white")
        b_left = sum(1 for c in self.coins if c.kind == "black")
        q_in_play = any(c.kind == "queen" for c in self.coins) or self.queen_pending_for is not None

        if (w_left == 0 or b_left == 0) and not q_in_play:
            self.phase = "OVER"
            if self.scores[0] > self.scores[1]:
                self.winner_banner = "White Wins!"
            elif self.scores[1] > self.scores[0]:
                self.winner_banner = "Black Wins!"
            else:
                self.winner_banner = "Match Tied!"
            self.last_note = self.winner_banner
            return

        if not shoot_again:
            self.turn = 1 - self.turn

        self.ready_striker_on_line()

    def process_input(self, mouse_xy):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                self.rack_new_game()

            if self.phase == "PLACE":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                    if self.spot_is_clear(self.striker.x, self.striker.y):
                        self.phase = "AIM"
                        self.aim_xy = [float(mouse_xy[0]), float(mouse_xy[1])]

            elif self.phase == "AIM":
                if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 3:
                    self.phase = "PLACE"
                elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1:
                    dx = self.striker.x - self.aim_xy[0]
                    dy = self.striker.y - self.aim_xy[1]
                    pull = math.hypot(dx, dy)
                    if pull > 10:
                        spd = min(MAX_STRIKE_POWER, (pull / 200.0) * MAX_STRIKE_POWER)
                        self.striker.vx = (dx / pull) * spd
                        self.striker.vy = (dy / pull) * spd
                        self.phase = "ROLLING"
                    else:
                        self.phase = "PLACE"

    def smooth_cursor_tracking(self, mouse_xy):
        if self.phase == "PLACE":
            clamped = max(self.lane_min_x, min(self.lane_max_x, float(mouse_xy[0])))
            if self.spot_is_clear(clamped, self.striker.y):
                self.target_striker_x = clamped
            nx = self.striker.x + (self.target_striker_x - self.striker.x) * 0.45
            if self.spot_is_clear(nx, self.striker.y):
                self.striker.x = nx

        elif self.phase == "AIM":
            self.aim_xy[0] += (mouse_xy[0] - self.aim_xy[0]) * 0.35
            self.aim_xy[1] += (mouse_xy[1] - self.aim_xy[1]) * 0.35

    def run(self):
        while True:
            mouse_xy = pygame.mouse.get_pos()
            self.process_input(mouse_xy)
            self.smooth_cursor_tracking(mouse_xy)

            if self.phase == "ROLLING":
                self.step_physics()

            for group in (self.sparks, self.ripples, self.toasts):
                for fx in list(group):
                    fx.tick()
                    if fx.life <= 0:
                        group.remove(fx)

            shake = (0, 0)
            if self.shake_frames > 0:
                shake = (
                    random.randint(-self.shake_frames, self.shake_frames),
                    random.randint(-self.shake_frames, self.shake_frames),
                )
                self.shake_frames = max(0, self.shake_frames - 1)

            self.screen.fill(BG_DARK)
            self.board.draw(self.screen, shake)

            if self.phase == "PLACE":
                self.board.highlight_active_lane(
                    self.screen, self.turn, self.lane_min_x, self.lane_max_x, shake
                )

            for rp in self.ripples:
                rp.draw(self.screen)

            for c in self.coins:
                c.draw(self.screen, shake)

            if self.striker.scale > 0:
                self.striker.draw(self.screen, shake)

            if self.phase == "AIM":
                self.hud.draw_aim_guide(self.screen, self.striker, self.coins, self.aim_xy)

            for sp in self.sparks:
                sp.draw(self.screen)
            for toast in self.toasts:
                toast.draw(self.screen)

            self.hud.draw_sidebar(self.screen, self, self.aim_xy)

            if self.phase == "OVER":
                self.hud.draw_winner_modal(self.screen, self.winner_banner)

            pygame.display.flip()
            self.clock.tick(FPS)
