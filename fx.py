# fx.py
import pygame
import math
import random
from text_helper import render_candy_text
from settings import CANDY_TOP, CANDY_BOT, CANDY_OUTLINE


class Spark:
    def __init__(self, x, y, color, speed_min=1.0, speed_max=6.0, size=4, life=28):
        angle = random.uniform(0, math.tau)
        spd = random.uniform(speed_min, speed_max)
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(angle) * spd
        self.vy = math.sin(angle) * spd
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life

    def tick(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.91
        self.vy *= 0.91
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return
        ratio = self.life / self.max_life
        alpha = int(255 * ratio)
        r = max(1, int(self.size * ratio))
        s = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (r, r), r)
        screen.blit(s, (int(self.x - r), int(self.y - r)))


class CalloutToast:
    # Bouncy 'Sodalicious! / Juicy! / Crush!' style candy text popup
    def __init__(self, x, y, message, accent_color=None, size=26):
        self.x = float(x)
        self.y = float(y)
        self.message = message
        self.life = 68
        self.max_life = 68

        # Customize gradient slightly for fouls vs positive callouts
        if accent_color and accent_color[0] > 180 and accent_color[1] < 80:
            # Red/Fiery Orange gradient for fouls
            self.surf = render_candy_text(
                message,
                size=size,
                top_color=(255, 190, 90),
                bot_color=(225, 45, 35),
                outline_color=(65, 12, 12),
            )
        else:
            # Signature Sodalicious Gold-to-Orange gradient
            self.surf = render_candy_text(
                message,
                size=size,
                top_color=CANDY_TOP,
                bot_color=CANDY_BOT,
                outline_color=CANDY_OUTLINE,
            )

    def tick(self):
        self.y -= 0.85
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return
        age = self.max_life - self.life
        # Bouncy pop-in scale animation on spawn
        if age < 8:
            scale = 0.6 + 0.55 * (age / 8.0)
        elif age < 14:
            scale = 1.15 - 0.15 * ((age - 8) / 6.0)
        else:
            scale = 1.0

        alpha = int(255 * min(1.0, (self.life / self.max_life) * 1.6))
        img = self.surf
        if abs(scale - 1.0) > 0.03:
            w = max(1, int(img.get_width() * scale))
            h = max(1, int(img.get_height() * scale))
            img = pygame.transform.smoothscale(img, (w, h))
        else:
            img = img.copy()

        img.set_alpha(alpha)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(img, rect)


class Ripple:
    def __init__(self, x, y, color, max_r=46):
        self.x = float(x)
        self.y = float(y)
        self.color = color
        self.r = 6.0
        self.max_r = float(max_r)
        self.life = 18
        self.max_life = 18

    def tick(self):
        self.r += (self.max_r - self.r) * 0.25
        self.life -= 1

    def draw(self, screen):
        if self.life <= 0:
            return
        alpha = int(195 * (self.life / self.max_life))
        dim = int(self.r * 2 + 6)
        s = pygame.Surface((dim, dim), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color, alpha), (dim // 2, dim // 2), int(self.r), 2)
        screen.blit(s, (int(self.x - dim // 2), int(self.y - dim // 2)))
