# boss_rumia.py
import pygame
import random
import math
import bullet_system
class Pattern:
    def __init__(self):
        self.active = False
        self.timer = 0

    def reset(self):
        self.active = True
        self.timer = 0

    def update(self, boss, bullet_system, player):
        pass

    def onGoing(self):
        return self.active

class RumiaPatternA(Pattern):
    def __init__(self):
        super().__init__()
        self.waveCount = 0

    def update(self, boss, bullet_system):
        if not self.active:
            return

        self.timer += 1

        if self.timer % 30 == 0 and self.waveCount < 2:

            cx = boss.x
            cy = boss.y

            for ring in range(3):
                speed = 2 + ring * 1.5

                for i in range(36):
                    angle = math.radians(i * 10)

                    bullet_system.spawn_custom(
                        cx,
                        cy,
                        math.cos(angle) * speed,
                        math.sin(angle) * speed
                    )

            self.waveCount += 1

        if self.waveCount >= 2:
            self.active = False


class Rumia:
    def __init__(self, screen_width):
        self.active = None
        self.x = screen_width // 2
        self.y = -80                  # start off-screen
        self.target_y = 80            # Touhou-style entry position
        self.skillDelay = 240
        self.skillCD = 240
        self.patterns = [
            RumiaPatternA(),

        ]
        self.currentPattern = None
        self.width = 48
        self.height = 64


        self.max_hp = 3000              #The amount of HP the Boss has
        self.hp = self.max_hp

        self.spawned = False
        self.dead = False

        self.phase = 1                # Phase 1 → Phase 2 at half HP

        # movement timing
        self.move_timer = 0
        self.move_cooldown = 180
        self.velocity = 2

    def spawn(self, screen_width=800):
        self.spawned = True
        self.y = -80
        self.active = True
        self.x = screen_width // 2

    def update(self, bullet_system):
        if not self.spawned or self.dead:
            return

        # Entry
        if self.y < self.target_y:
            self.y += 2
            return

        # Phase switch
        if self.hp <= self.max_hp // 2:
            self.phase = 2

        # Pattern cooldown
        self.skillDelay -= 1

        if self.skillDelay <= 0:
            self.skillDelay = self.skillCD

            available = [p for p in self.patterns if not p.onGoing()]
            if available:
                self.currentPattern = random.choice(available)
                self.currentPattern.reset()

        if self.currentPattern:
            self.currentPattern.update(self, bullet_system)

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

        # HP bar
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (255, 0, 0), (100, 20, 600 * hp_ratio, 8))
