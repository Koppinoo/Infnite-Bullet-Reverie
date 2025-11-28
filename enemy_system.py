import pygame
import random
import math

# --- Enemy class with movement patterns ---
class Enemy:
    def __init__(
        self,
        x,
        y,
        width=32,
        height=32,
        speed=2,
        health=1,
        pattern="straight",
        screen_width=800
    ):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.health = health

        # pattern stuff
        self.pattern = pattern
        self.screen_width = screen_width

        # store spawn time & base position for fancy movement
        self.spawn_time = pygame.time.get_ticks()
        self.base_x = x

        # randomised params for variety
        self.direction = random.choice([-1, 1])          # used for diagonal / zigzag
        self.amplitude = random.randint(30, 80)          # used for sine / zigzag
        self.frequency = random.uniform(1.0, 2.5)        # used for sine

    def update(self):
        """
        Update enemy position based on its movement pattern.
        """
        # time in seconds since spawn (for smooth sine movement)
        t = (pygame.time.get_ticks() - self.spawn_time) / 1000.0

        if self.pattern == "straight":
            # simple downward movement
            self.y += self.speed

        elif self.pattern == "diagonal":
            # down + slight horizontal drift
            self.y += self.speed
            self.x += self.direction * self.speed * 0.6

        elif self.pattern == "sine":
            # down + smooth sine wave left/right
            self.y += self.speed
            self.x = self.base_x + math.sin(t * self.frequency * 2 * math.pi) * self.amplitude

        elif self.pattern == "zigzag":
            # “chunky” zigzag using sine sign
            self.y += self.speed

            # sign of sine: flips direction periodically
            zig = math.sin(t * self.frequency * 2 * math.pi)
            self.x = self.base_x + math.copysign(self.amplitude, zig)

            # clamp so they don't go off screen too far
            if self.x < 0:
                self.x = 0
            if self.x + self.width > self.screen_width:
                self.x = self.screen_width - self.width

        else:
            # fallback: straight
            self.y += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.x, self.y, self.width, self.height))


# --- Enemy system ---
class EnemySystem:
    def __init__(self, screenWidth, screenHeight):
        self.enemies = []  # list to hold active enemies
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.spawnCooldown = 1000  # milliseconds between spawns
        self.lastSpawnTime = pygame.time.get_ticks()  # last time an enemy was spawned

        # which patterns can be used for random spawns
        self.available_patterns = ["straight", "diagonal", "sine",]

    def spawnEnemy(self, pattern=None):
        """
        Spawns a single enemy at the top with an optional movement pattern.
        If pattern is None, a random one from available_patterns is chosen.
        """
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastSpawnTime > self.spawnCooldown:
            # Random horizontal position at the top of the screen
            x = random.randint(0, self.screenWidth - 32)
            y = -32  # start off-screen

            if pattern is None:
                pattern = random.choice(self.available_patterns)

            enemy = Enemy(
                x,
                y,
                width=32,
                height=32,
                speed=2,
                health=1,
                pattern=pattern,
                screen_width=self.screenWidth,
            )
            self.enemies.append(enemy)
            self.lastSpawnTime = currentTime

    def updateEnemies(self):
        for enemy in self.enemies:
            enemy.update()
        # Remove enemies that go off-screen
        self.enemies = [e for e in self.enemies if e.y < self.screenHeight + e.height]

    def drawEnemies(self, screen):
        for enemy in self.enemies:
            enemy.draw(screen)
