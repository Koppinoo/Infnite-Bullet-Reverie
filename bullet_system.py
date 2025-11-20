import pygame

class BulletSystem:
    def __init__(self, bulletSpeed=10, shootCooldown=200):
        # List to store active bullets
        self.bullets = []

        # Shooting rate
        self.bulletSpeed = bulletSpeed
        self.shootCooldown = shootCooldown

        # Time of last bullet fired
        self.lastShotTime = 0

    def shoot(self, playerX, playerY, playerSize):
        currentTime = pygame.time.get_ticks()

        # Check cooldown
        if currentTime - self.lastShotTime >= self.shootCooldown:
            bulletX = playerX + playerSize // 2 - 4   # center of player
            bulletY = playerY

            self.bullets.append([bulletX, bulletY])
            self.lastShotTime = currentTime

    def updateBullets(self):
        # Move bullets upward
        for bullet in self.bullets:
            bullet[1] -= self.bulletSpeed

        # Remove bullets that leave the screen
        self.bullets = [b for b in self.bullets if b[1] > -10]

    def drawBullets(self, screen):
        # Draw each bullet
        for bullet in self.bullets:
            pygame.draw.rect(screen, (255, 255, 0), (bullet[0], bullet[1], 8, 8))
