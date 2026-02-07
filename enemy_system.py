
import pygame
import random
import math
from bullet_system import BulletSystem

# ----------------------------
# Touhou-inspired enemy types
# ----------------------------

class Enemy:
    """
    Base enemy class (Touhou-style):
    - position (x, y)
    - direction vector (dx, dy)
    - velocity (speed scalar)
    - hp (health)
    - elapsed_frames (for scripted behaviour)
    """
    def __init__(self, x, y, direction=(0, 1), velocity=1.0, hp=1, width=32, height=32, screen_width=800):
        self.x = float(x)
        self.y = float(y)
        self.width = width
        self.height = height

        self.direction = pygame.Vector2(direction)
        if self.direction.length_squared() == 0:
            self.direction = pygame.Vector2(0, 1)
        # normalise so velocity is consistent
        self.direction = self.direction.normalize()

        self.velocity = float(velocity)
        self.health = int(hp)   # keep 'health' for your main collision code
        self.hp = int(hp)       # also store 'hp' for Touhou terminology

        self.elapsed_frames = 0
        self.alive = True
        self.screen_width = screen_width

    def got_hit(self, damage=1):
        self.health -= damage
        self.hp = self.health
        if self.health <= 0:
            self.alive = False

    def update(self, player_pos=None, enemy_bullets: BulletSystem | None = None):
        """Default behaviour: move linearly along direction."""
        if not self.alive:
            return
        self.x += self.direction.x * self.velocity
        self.y += self.direction.y * self.velocity
        self.elapsed_frames += 1

    def draw(self, screen):
        # Simple placeholder sprite (filled rect). Replace later with images if desired.
        pygame.draw.rect(screen, (60, 140, 255), (int(self.x), int(self.y), self.width, self.height))


class BlueFairy(Enemy):
    """Basic enemy: straight movement, 1 HP."""
    def __init__(self, x, y, direction=(0, 1), velocity=1.0, screen_width=800):
        super().__init__(x, y, direction=direction, velocity=velocity, hp=1, screen_width=screen_width)

    def draw(self, screen):
        pygame.draw.rect(screen, (60, 140, 255), (int(self.x), int(self.y), self.width, self.height))


class PinkFairy(Enemy):
    """
    PinkFairy: more health and scripted pause window (Touhou-like)
    - HP: 4
    - At frame 90: choose left/right drift and slow down.
    - Frames 91-120: pause (reserved for shooting later)
    """
    def __init__(self, x, y, direction=(0, 1), velocity=1.0, screen_width=800):
        super().__init__(x, y, direction=direction, velocity=velocity, hp=4, screen_width=screen_width)
        self.base_velocity = self.velocity

    def update(self, player_pos=None, enemy_bullets: BulletSystem | None = None):
        if not self.alive:
            return

        self.elapsed_frames += 1

        # Pause window (Touhou: >90 and <=120 return)
        if 90 < self.elapsed_frames <= 120:
            return

        if self.elapsed_frames == 90:
            # Pick drift direction based on which side of screen you're on (Touhou logic)
            half = (self.screen_width - 1) / 2
            self.direction = pygame.Vector2(1, 0) if self.x >= half else pygame.Vector2(-1, 0)
            self.velocity *= 0.5  # slow down

            # Shooting would occur here later (fan toward player). Keeping placeholder for now.
            # if enemy_bullets and player_pos: ...

        # Movement: Touhou uses velocity * elapsedTime / 75.0 (accelerating feeling)
        scale = max(self.elapsed_frames / 75.0, 0.25)
        self.x += self.direction.x * self.velocity * scale
        self.y += self.direction.y * self.velocity * scale

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 110, 190), (int(self.x), int(self.y), self.width, self.height))


class PinkFairyGood(Enemy):
    """
    PinkFairyGood: stronger variant
    - HP: 8
    - Shoots at frames 90 and 120 (later)
    - Pauses between 91 and 150
    """
    def __init__(self, x, y, direction=(0, 1), velocity=1.0, screen_width=800):
        super().__init__(x, y, direction=direction, velocity=velocity, hp=8, screen_width=screen_width)
        self.base_velocity = self.velocity

    def update(self, player_pos=None, enemy_bullets: BulletSystem | None = None):
        if not self.alive:
            return

        self.elapsed_frames += 1

        # Shooting triggers (placeholder)
        if self.elapsed_frames in (90, 120):
            half = (self.screen_width - 1) / 2
            self.direction = pygame.Vector2(1, 0) if self.x >= half else pygame.Vector2(-1, 0)
            self.velocity *= 0.5

            # Shooting would occur here later.

        # Pause window
        if 90 < self.elapsed_frames <= 150:
            return

        scale = max(self.elapsed_frames / 75.0, 0.25)
        self.x += self.direction.x * self.velocity * scale
        self.y += self.direction.y * self.velocity * scale

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 80, 140), (int(self.x), int(self.y), self.width, self.height))


# ----------------------------
# Enemy manager (EnemySystem)
# ----------------------------

class EnemySystem:
    """
    Touhou-inspired EnemySystem / EnemyManager:
    - Keeps active enemies list
    - Spawns different enemy types
    - Updates & draws enemies
    """
    def __init__(self, screenWidth, screenHeight):
        self.enemies: list[Enemy] = []
        self.screenWidth = int(screenWidth)
        self.screenHeight = int(screenHeight)

        # Difficulty knobs (controlled by WaveSystem)
        self.baseVelocity = 1.0

    def spawn(self, enemy_type: str, x: float, y: float, direction=(0, 1), velocity: float | None = None):
        """Spawn a specific enemy type at position."""
        v = self.baseVelocity if velocity is None else float(velocity)
        if enemy_type == "BlueFairy":
            e = BlueFairy(x, y, direction=direction, velocity=v, screen_width=self.screenWidth)
        elif enemy_type == "PinkFairy":
            e = PinkFairy(x, y, direction=direction, velocity=v, screen_width=self.screenWidth)
        elif enemy_type == "PinkFairyGood":
            e = PinkFairyGood(x, y, direction=direction, velocity=v, screen_width=self.screenWidth)
        else:
            e = Enemy(x, y, direction=direction, velocity=v, hp=1, screen_width=self.screenWidth)

        self.enemies.append(e)

    def updateEnemies(self, bullet_system: BulletSystem | None = None, player_x=None, player_y=None, player_size=32):
        player_pos = None
        if player_x is not None and player_y is not None:
            player_pos = pygame.Vector2(player_x + player_size/2, player_y + player_size/2)

        for e in self.enemies:
            e.update(player_pos=player_pos, enemy_bullets=bullet_system)

        # Remove dead or out-of-bounds enemies (Touhou: keep only in playfield)
        new_list = []
        for e in self.enemies:
            if not e.alive:
                continue
            # allow enemies to travel off bottom slightly before removing
            if e.y > self.screenHeight + e.height:
                continue
            if e.x < -e.width or e.x > self.screenWidth + e.width:
                continue
            new_list.append(e)
        self.enemies = new_list

    def drawEnemies(self, screen):
        for e in self.enemies:
            e.draw(screen)
