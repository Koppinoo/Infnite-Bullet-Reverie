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

class RumiaPatternB(Pattern):
    def __init__(self):
        super().__init__()
        self.wave = 0

    def reset(self):
        super().reset()
        self.wave = 0

    def update(self, boss, bullet_system):
        if not self.active:
            return

        self.timer += 1

        # Fire every 10 frames
        if self.timer % 10 == 0 and self.wave < 16:

            cx = boss.x
            cy = boss.y

            baseAngle = math.radians(self.wave * 5)

            for i in range(18):
                angle = baseAngle + math.radians(i * 20)

                bullet_system.spawn_custom(
                    cx,
                    cy,
                    math.cos(angle) * 4,
                    math.sin(angle) * 4
                )

            self.wave += 1

        # End after 16 waves
        if self.wave >= 16:
            self.active = False


class RumiaPatternC(Pattern):
    def __init__(self):
        super().__init__()
        self.fired = 0
        self.rotation = 0

    def reset(self):
        super().reset()
        self.fired = 0
        self.rotation = 0

    def update(self, boss, bullet_system):
        if not self.active:
            return

        self.timer += 1

        # Fire every 2 frames
        if self.timer % 2 == 0 and self.fired < 256:

            cx = boss.x
            cy = boss.y

            for i in range(4):
                angle = math.radians(self.rotation + i * 90)

                bullet_system.spawn_custom(
                    cx,
                    cy,
                    math.cos(angle) * 5,
                    math.sin(angle) * 5
                )

            self.rotation += 5
            self.fired += 4

        if self.fired >= 256:
            self.active = False


class RumiaPatternD(Pattern):
    def __init__(self):
        super().__init__()
        self.wave = 0
        self.storedBullets = []
        self.redirected = False

    def reset(self):
        super().reset()
        self.wave = 0
        self.storedBullets = []
        self.redirected = False

    def update(self, boss, bullet_system):
        if not self.active:
            return

        self.timer += 1

        cx = boss.x
        cy = boss.y

        # Spawn 2 waves of 37 bullets
        if self.timer % 60 == 0 and self.wave < 2:
            for i in range(37):
                angle = math.radians(i * (360 / 37))

                bullet = bullet_system.spawn_custom(
                    cx,
                    cy,
                    math.cos(angle) * 3,
                    math.sin(angle) * 3
                )

                self.storedBullets.append(bullet)

            self.wave += 1

        # Stop bullets at frame 120
        if self.timer == 120:
            for bullet in self.storedBullets:
                bullet.vx = 0
                bullet.vy = 0

        # Redirect at frame 150
        if self.timer == 150 and not self.redirected:
            for bullet in self.storedBullets:
                dx = boss.player_x - bullet.x
                dy = boss.player_y - bullet.y
                length = math.hypot(dx, dy)
                if length != 0:
                    bullet.vx = (dx / length) * 6
                    bullet.vy = (dy / length) * 6
            self.redirected = True

        if self.timer > 200:
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
            RumiaPatternB(),
            RumiaPatternC(),
            RumiaPatternD(),
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

    def update(self, bullet_system,player):


        self.player_x = player["x"]
        self.player_y = player["y"]

        if not self.spawned or self.dead:
            return

        # Entry
        if self.y < self.target_y:
            self.y += 2
            return

        # Phase switch
        if self.hp <= self.max_hp // 2:
            self.phase = 2

        #In order to stop cooldown overlap
        if self.currentPattern and self.currentPattern.onGoing():
            self.currentPattern.update(self, bullet_system)
            return

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

def update(self, bullet_system, player):

    # Store player position for use in attack calculations
    self.player_x = player["x"]
    self.player_y = player["y"]

    # Prevent updates if boss not active
    if not self.spawned or self.dead:
        return

    # Controlled descent into arena
    if self.y < self.target_y:
        self.y += 2
        return
