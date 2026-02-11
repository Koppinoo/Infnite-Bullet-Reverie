
import pygame
import random
import math




ENEMY_PROFILES = {
    "BlueFairy": {
        "hp": 1,
        "strafeSpeed": 2.0,
        "strafeDuration": 1200,
    },
    "PinkFairy": {
        "hp": 4,
        "strafeSpeed": 1.6,
        "strafeDuration": 2000,
    },
    "PinkFairyGood": {
        "hp": 8,
        "strafeSpeed": 1.4,
        "strafeDuration": 2600,
    }
}


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
        self.alive = True  # Used to safely remove enemies when they exit the playfield

        # movement
        self.speed = speed
        self.movement_pattern = movement_pattern
        self.screen_width = screen_width

        # movement scripting
        self.spawnTime = pygame.time.get_ticks()

        # Movement scripting
        self.pattern = "enter_strafe_exit"  # default
        self.targetY = y + 120  # where enemy stops descending
        self.phase = 0  # 0=enter, 1=strafe, 2=exit
        self.phaseStart = self.spawnTime

        self.strafeDir = 1  # 1 right, -1 left
        self.strafeSpeed = 2.0
        self.enterSpeed = self.speed
        self.exitSpeed = self.speed + 1.0

        self.strafeDuration = 1500  # ms

        # enemy health
        self.health = health

        # store when spawned for pattern timing
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
        now = pygame.time.get_ticks()

        # Phase 0: Enter from top
        if self.phase == 0:
            self.y += self.enterSpeed
            if self.y >= self.targetY:
                self.y = self.targetY
                self.phase = 1
                self.phaseStart = now

        # Phase 1: Horizontal movement (scripted)
        elif self.phase == 1:
            self.x += self.strafeDir * self.strafeSpeed

            if self.x <= 0 or self.x + self.width >= self.screen_width:
                self.strafeDir *= -1

            if now - self.phaseStart >= self.strafeDuration:
                self.phase = 2
                self.phaseStart = now

        # Phase 2: Exit upward (Touhou-style clear)
        elif self.phase == 2:
            self.y -= self.exitSpeed
            if self.y + self.height < 0:
                self.alive = False

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
        self.enemySpeed = 2.0  # base speed for enemies
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.spawnCooldown = 1000  # ms between spawns
        self.lastSpawnTime = pygame.time.get_ticks()


        # Patterns to randomly choose from

        self.bullet_patterns = ["aimed", "radial", "spread", "spiral"]

    def spawnEnemy(self, enemy_type="BlueFairy", targetY=120, bullet_pattern=None):
        """
        Spawns an enemy based on a named profile (BlueFairy / PinkFairy / PinkFairyGood).
        This matches WaveSystem calling spawnEnemy(enemy_type=..., targetY=...).
        """
        now = pygame.time.get_ticks()

        # Choose profile safely (fallback to BlueFairy if typo)
        profile = ENEMY_PROFILES.get(enemy_type, ENEMY_PROFILES["BlueFairy"])

        # Random X spawn, spawn just above screen
        x = random.randint(0, self.screenWidth - 32)
        y = -32

        # Decide bullet pattern per enemy type (simple + deterministic)
        if bullet_pattern is None:
            if enemy_type == "BlueFairy":
                bullet_pattern = "aimed"  # can be slow / rare shots
            elif enemy_type == "PinkFairy":
                bullet_pattern = "aimed"  # basic aimed shots first
            else:
                bullet_pattern = "spread"  # slightly harder later

        enemy = Enemy(
            x,
            y,
            width=32,
            height=32,
            speed=self.enemySpeed,
            health=profile["hp"],
            bullet_pattern=bullet_pattern,
            screen_width=self.screenWidth,
        )

        # Apply profile movement settings
        enemy.strafeSpeed = profile["strafeSpeed"]
        enemy.strafeDuration = profile["strafeDuration"]
        enemy.targetY = targetY

        # Make shooting actually noticeable while testing (ms)
        if enemy_type == "BlueFairy":
            enemy.shoot_cooldown = 2000
        elif enemy_type == "PinkFairy":
            enemy.shoot_cooldown = 900
        else:
            enemy.shoot_cooldown = 700

        enemy.last_shot_time = now
        self.enemies.append(enemy)
        self.lastSpawnTime = now

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
            if getattr(e, "alive", True) and e.y < self.screenHeight + e.height
        ]

    def drawEnemies(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
