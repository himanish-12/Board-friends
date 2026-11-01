# effects.py
import pygame
import math
import random
from font_renderer import get_font


class Particle:
    def __init__(self, x, y, color, speed_min=1, speed_max=6, size=4, life=30):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(speed_min, speed_max)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.92
        self.vy *= 0.92
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        r = max(1, int(self.size * (self.life / self.max_life)))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r, r), r)
        surface.blit(s, (int(self.x - r), int(self.y - r)))


class FloatingText:
    def __init__(self, x, y, text, color, size=22):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 60
        self.max_life = 60
        self.font = get_font("Segoe UI", size, bold=True)

    def update(self):
        self.y -= 1.1
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(255 * (self.life / self.max_life))
        txt_surf = self.font.render(self.text, True, self.color)
        txt_surf.set_alpha(alpha)
        rect = txt_surf.get_rect(center=(int(self.x), int(self.y)))
        surface.blit(txt_surf, rect)


class Shockwave:
    def __init__(self, x, y, color, max_r=45):
        self.x = x
        self.y = y
        self.color = color
        self.r = 5
        self.max_r = max_r
        self.life = 18
        self.max_life = 18

    def update(self):
        self.r += (self.max_r - self.r) * 0.25
        self.life -= 1

    def draw(self, surface):
        if self.life <= 0:
            return
        alpha = int(200 * (self.life / self.max_life))
        s = pygame.Surface((int(self.r * 2 + 4), int(self.r * 2 + 4)), pygame.SRCALPHA)
        pygame.draw.circle(
            s, (*self.color, alpha), (int(self.r + 2), int(self.r + 2)), int(self.r), 2
        )
        surface.blit(s, (int(self.x - self.r - 2), int(self.y - self.r - 2)))
