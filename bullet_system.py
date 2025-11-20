import pygame

class Bullet:
    def __init__(self, x, y, width=8, height=8, speed=10):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed

    def update(self):
        self.y -= self.speed  # player bullets move up

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 255, 0), (self.x, self.y, self.width, self.height))

class BulletSystem:
    def __init__(self, bulletSpeed=10, shootCooldown=200):
        self.bullets = []
        self.bulletSpeed = bulletSpeed
        self.shootCooldown = shootCooldown
        self.lastShotTime = 0

    def shoot(self, playerX, playerY, playerSize):
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastShotTime >= self.shootCooldown:
            bulletX = playerX + playerSize // 2 - 4
            bulletY = playerY
            self.bullets.append(Bullet(bulletX, bulletY, speed=self.bulletSpeed))
            self.lastShotTime = currentTime

    def updateBullets(self):
        for bullet in self.bullets:
            bullet.update()
        self.bullets = [b for b in self.bullets if b.y > -10]

    def drawBullets(self, screen):
        for bullet in self.bullets:
            bullet.draw(screen)
