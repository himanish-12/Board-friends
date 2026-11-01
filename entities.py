# entities.py
import pygame
import math
from config import GOLD


class Disc:
    def __init__(self, x, y, radius, mass, color, disc_type):
        self.x = float(x)
        self.y = float(y)
        self.vx = 0.0
        self.vy = 0.0
        self.radius = radius
        self.mass = mass
        self.color = color
        self.disc_type = disc_type  # 'white', 'black', 'queen', 'striker'
        self.trail = []
        self.pocketing = False
        self.pocket_target = None
        self.scale = 1.0

    @property
    def speed(self):
        return math.hypot(self.vx, self.vy)

    @property
    def is_moving(self):
        return self.speed > 0 or self.pocketing

    def update_trail(self):
        if self.speed > 2.5 and not self.pocketing:
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:
                self.trail.pop(0)
        elif self.trail:
            self.trail.pop(0)

    def draw(self, surface, offset=(0, 0)):
        ox, oy = offset
        # Motion trail
        for i, (tx, ty) in enumerate(self.trail):
            ratio = (i + 1) / len(self.trail)
            tr = max(2, int(self.radius * self.scale * ratio * 0.75))
            alpha = int(90 * ratio)
            s = pygame.Surface((tr * 2, tr * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (tr, tr), tr)
            surface.blit(s, (int(tx - tr + ox), int(ty - tr + oy)))

        r = max(2, int(self.radius * self.scale))
        cx, cy = int(self.x + ox), int(self.y + oy)

        # Drop shadow
        if not self.pocketing:
            shadow_s = pygame.Surface((r * 2 + 6, r * 2 + 6), pygame.SRCALPHA)
            pygame.draw.circle(shadow_s, (0, 0, 0, 65), (r + 3, r + 3), r)
            surface.blit(shadow_s, (cx - r, cy - r + 3))

        # Main Disc Body
        pygame.draw.circle(surface, self.color, (cx, cy), r)

        # Decorative ridges & details
        if self.disc_type == "white":
            pygame.draw.circle(surface, (215, 208, 195), (cx, cy), int(r * 0.72), 2)
            pygame.draw.circle(surface, (190, 180, 165), (cx, cy), r, 2)
            pygame.draw.circle(
                surface,
                (255, 255, 255),
                (cx - int(r * 0.25), cy - int(r * 0.25)),
                max(1, int(r * 0.15)),
            )
        elif self.disc_type == "black":
            pygame.draw.circle(surface, (75, 78, 85), (cx, cy), int(r * 0.72), 2)
            pygame.draw.circle(surface, (20, 20, 24), (cx, cy), r, 2)
            pygame.draw.circle(
                surface,
                (110, 115, 125),
                (cx - int(r * 0.25), cy - int(r * 0.25)),
                max(1, int(r * 0.15)),
            )
        elif self.disc_type == "queen":
            pygame.draw.circle(surface, GOLD, (cx, cy), int(r * 0.65), 2)
            pygame.draw.circle(surface, GOLD, (cx, cy), int(r * 0.25))
            pygame.draw.circle(surface, (130, 15, 30), (cx, cy), r, 2)
        elif self.disc_type == "striker":
            pygame.draw.circle(surface, (240, 248, 255), (cx, cy), int(r * 0.78), 2)
            pygame.draw.circle(surface, GOLD, (cx, cy), int(r * 0.45), 2)
            pygame.draw.circle(surface, (255, 255, 255), (cx, cy), int(r * 0.18))
            pygame.draw.circle(surface, (30, 95, 145), (cx, cy), r, 3)
