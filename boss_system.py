# boss_rumia.py
import pygame
import random



class Rumia:
    def __init__(self, screen_width):
        self.active = None
        self.x = screen_width // 2
        self.y = -80                  # start off-screen
        self.target_y = 80            # Touhou-style entry position

        self.width = 48
        self.height = 64

        self.max_hp = 3000
        self.hp = self.max_hp

        self.spawned = False
        self.dead = False

        self.phase = 1                # Phase 1 → Phase 2 at half HP

        # movement timing
        self.move_timer = 0
        self.move_cooldown = 180

    def spawn(self, screen_width=800):
        self.spawned = True
        self.y = -80
        self.active = True
        self.x = screen_width // 2

    def update(self):
        if not self.spawned or self.dead:
            return

        # --- Entry movement ---
        if self.y < self.target_y:
            self.y += 2
            return

        # --- Phase change ---
        if self.hp <= self.max_hp // 2:
            self.phase = 2

        # --- Idle movement placeholder ---
        self.move_timer += 1
        if self.move_timer >= self.move_cooldown:
            self.move_timer = 0
            self.x = random.randint(100, 700)

    def draw(self, screen):
        if not self.spawned:
            return

        pygame.draw.rect(
            screen,
            (200, 50, 200),
            (self.x - self.width//2, self.y, self.width, self.height)
        )

