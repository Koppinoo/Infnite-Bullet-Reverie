import pygame
import random
import math
    
from bullet_system import BulletSystem  # only for type hints / clarity


class Enemy:
    def __init__(
        self,
        x,
        y,
        width=32,
        height=32,
        speed=2,
        health=1,
        movement_pattern="straight",
        bullet_pattern="aimed",
        screen_width=800,
    ):
        # position / size
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height

        # movement
        self.speed = speed
        self.movement_pattern = movement_pattern
        self.screen_width = screen_width

        # enemy health
        self.health = health

        # store when spawned for pattern timing
        self.spawn_time = pygame.time.get_ticks()
        self.base_x = x

        # shooting
        self.bullet_pattern = bullet_pattern
        self.shoot_cooldown = random.randint(800, 1600)  # ms
        self.last_shot_time = pygame.time.get_ticks()

        # enemy death feedback

        self.dying = False
        self.death_start_time = 0
        self.death_duration = 300  # milliseconds

    # ---------- MOVEMENT ----------

    def update_position(self):
        """
     predictable downward movement.
        This improves readability and ensures enemy behaviour
        is consistent and easy to understand.
        """
        self.y += self.speed

    # ---------- SHOOTING ----------

    def try_shoot(self, bullet_system: "BulletSystem", player_x, player_y, player_size):
        """Attempt to shoot based on cooldown and chosen bullet pattern."""
        now = pygame.time.get_ticks()
        if now - self.last_shot_time < self.shoot_cooldown:
            return

        self.last_shot_time = now

        # Enemy centre
        cx = self.x + self.width / 2
        cy = self.y + self.height / 2

        # Player centre
        px = player_x + player_size / 2
        py = player_y + player_size / 2

        pattern = self.bullet_pattern

        if pattern == "aimed":
            # sniper shot at player
            bullet_system.shoot_aimed(cx, cy, px, py)

        elif pattern == "radial":
            # full flower burst
            bullet_system.shoot_radial(cx, cy, count=16)

        elif pattern == "spread":
            # fan towards downward direction (pi/2)
            base_angle = math.pi / 2
            bullet_system.shoot_spread(
                cx, cy, base_angle,
                spread_angle=math.radians(60),
                count=9
            )

        elif pattern == "spiral":
            # rotating spiral that evolves over time
            bullet_system.shoot_spiral(cx, cy, count=8, step=0.25)

        else:
            # default: aimed
            bullet_system.shoot_aimed(cx, cy, px, py)

    # ---------- DRAW ----------

    def draw(self, screen):
        if self.dying:
            elapsed = pygame.time.get_ticks() - self.death_start_time
            progress = min(elapsed / self.death_duration, 1)

            max_radius = self.width
            radius = int(max_radius * progress)

            # Semi-transparent blue expanding circle
            surface = pygame.Surface((max_radius * 2, max_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(
                surface,
                (80, 160, 255, 120),  # RGBA blue
                (max_radius, max_radius),
                radius
            )

            screen.blit(
                surface,
                (
                    self.x + self.width // 2 - max_radius,
                    self.y + self.height // 2 - max_radius
                )
            )
        else:
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                pygame.Rect(int(self.x), int(self.y), self.width, self.height)
            )


class EnemySystem:
    def __init__(self, screenWidth, screenHeight):
        self.enemies = []
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.spawnCooldown = 1000  # ms between spawns
        self.lastSpawnTime = pygame.time.get_ticks()

        # Patterns to randomly choose from
        self.movement_patterns = ["straight", "diagonal", "sine", "zigzag"]
        self.bullet_patterns = ["aimed", "radial", "spread", "spiral"]

    def spawnEnemy(self, movement_pattern=None, bullet_pattern=None):
        """Spawn a single enemy at top of screen with optional patterns."""
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastSpawnTime <= self.spawnCooldown:
            return

        x = random.randint(0, self.screenWidth - 32)
        y = -32

        if movement_pattern is None:
            movement_pattern = random.choice(self.movement_patterns)
        if bullet_pattern is None:
            bullet_pattern = random.choice(self.bullet_patterns)

        enemy = Enemy(
            x,
            y,
            width=32,
            height=32,
            speed=2,
            health=1,
            movement_pattern=movement_pattern,
            bullet_pattern=bullet_pattern,
            screen_width=self.screenWidth,
        )
        self.enemies.append(enemy)
        self.lastSpawnTime = currentTime

    def updateEnemies(self, bullet_system: "BulletSystem" = None,
                      player_x=None, player_y=None, player_size=32):
        """Update positions and optionally have them fire bullets."""
        for enemy in self.enemies:
            enemy.update_position()
            if bullet_system is not None and player_x is not None and player_y is not None:
                enemy.try_shoot(bullet_system, player_x, player_y, player_size)

        # Remove enemies that move off the bottom of the screen
        self.enemies = [
            e for e in self.enemies
            if e.y < self.screenHeight + e.height
        ]

    def drawEnemies(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
