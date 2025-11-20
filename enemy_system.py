import pygame
import random

# --- Enemy class ---
class Enemy:
        def __init__(self, x, y, width=32, height=32, speed=2, health=1):
            self.x = x
            self.y = y
            self.width = width
            self.height = height
            self.speed = speed
            self.health = health

        def update(self):
            self.y += self.speed  # moves downward
            # you can add horizontal movement or patterns later

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

    def spawnEnemy(self):
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastSpawnTime > self.spawnCooldown:
            # Random horizontal position at the top of the screen
            x = random.randint(0, self.screenWidth - 32)
            y = -32  # start off-screen
            enemy = Enemy(x, y)
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
