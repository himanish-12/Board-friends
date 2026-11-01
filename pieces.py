# pieces.py
import pygame
import math
from settings import GOLD, IVORY, CHARCOAL, QUEEN_RED, STRIKER_TEAL


class CarromPiece:
    def __init__(self, x, y, radius, mass, color, kind):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.mass = mass
        self.color = color
        self.kind = kind  # 'white', 'black', 'queen', or 'striker'
        self.trail = []
        self.falling_in = False
        self.pocket_xy = None
        self.scale = 1.0

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)

    @property
    def in_motion(self):
        return self.speed > 0 or self.falling_in

    def record_trail(self):
        if self.speed > 2.8 and not self.falling_in:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 9:
                self.trail.pop(0)
        elif self.trail:
            self.trail.pop(0)

    def draw(self, screen, shake=(0, 0)):
        ox, oy = shake

        # Motion blur behind fast shots
        for idx, (tx, ty) in enumerate(self.trail):
            t_ratio = (idx + 1) / len(self.trail)
            tr = max(2, int(self.radius * self.scale * t_ratio * 0.72))
            s = pygame.Surface((tr * 2, tr * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(80 * t_ratio)), (tr, tr), tr)
            screen.blit(s, (int(tx - tr + ox), int(ty - tr + oy)))

        r = max(2, int(self.radius * self.scale))
        cx, cy = int(round(self.x + ox)), int(round(self.y + oy))

        # Soft table shadow
        if not self.falling_in:
            sh = pygame.Surface((r * 2 + 8, r * 2 + 8), pygame.SRCALPHA)
            pygame.draw.circle(sh, (0, 0, 0, 75), (r + 4, r + 4), r)
            screen.blit(sh, (cx - r - 1, cy - r + 2))

        # Classic turned-wood concentric grooves
        pygame.draw.circle(screen, self.color, (cx, cy), r)

        if self.kind == "white":
            pygame.draw.circle(screen, (218, 210, 194), (cx, cy), int(r * 0.75), 2)
            pygame.draw.circle(screen, (200, 190, 172), (cx, cy), int(r * 0.38), 1)
            pygame.draw.circle(screen, (175, 164, 148), (cx, cy), r, 2)
            pygame.draw.circle(screen, (255, 255, 255), (cx - int(r * 0.28), cy - int(r * 0.28)), max(1, int(r * 0.14)))
        elif self.kind == "black":
            pygame.draw.circle(screen, (72, 76, 84), (cx, cy), int(r * 0.75), 2)
            pygame.draw.circle(screen, (58, 62, 70), (cx, cy), int(r * 0.38), 1)
            pygame.draw.circle(screen, (20, 22, 26), (cx, cy), r, 2)
            pygame.draw.circle(screen, (115, 120, 132), (cx - int(r * 0.28), cy - int(r * 0.28)), max(1, int(r * 0.14)))
        elif self.kind == "queen":
            pygame.draw.circle(screen, GOLD, (cx, cy), int(r * 0.68), 2)
            pygame.draw.circle(screen, GOLD, (cx, cy), int(r * 0.26))
            pygame.draw.circle(screen, (125, 16, 28), (cx, cy), r, 2)
        elif self.kind == "striker":
            pygame.draw.circle(screen, (238, 246, 255), (cx, cy), int(r * 0.78), 2)
            pygame.draw.circle(screen, GOLD, (cx, cy), int(r * 0.48), 2)
            pygame.draw.circle(screen, (255, 255, 255), (cx, cy), int(r * 0.18))
            pygame.draw.circle(screen, (28, 92, 138), (cx, cy), r, 3)
