import pygame
import math

class Bullet:
    def __init__(self, x, y, vx, vy, width=8, height=8, color=(255, 255, 0)):
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.width = width
        self.height = height
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.rect(
            screen,
            self.color,
            pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        )

class EnemyBullet:
    def __init__(self, x, y, vx, vy):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.width = 6
        self.height = 6

    def update(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.x, self.y, self.width, self.height))


class BulletSystem:
    def __init__(self, bulletSpeed=10, shootCooldown=150, screenWidth=800, screenHeight=600):
        self.bullets = []
        self.bulletSpeed = bulletSpeed
        self.shootCooldown = shootCooldown
        self.lastShotTime = 0
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight

        # used for spiral patterns (each BulletSystem instance has its own)
        self.spiral_angle = 0.0

    # ---------- PLAYER SHOOTING (keeps old API .shoot) ----------

    def shoot(self, playerX, playerY, playerSize):
        """Fire a single bullet straight up from player centre."""
        currentTime = pygame.time.get_ticks()
        if currentTime - self.lastShotTime < self.shootCooldown:
            return

        bulletX = playerX + playerSize // 2 - 4
        bulletY = playerY
        # straight up: vy negative
        self.bullets.append(
            Bullet(
                bulletX,
                bulletY,
                vx=0,
                vy=-self.bulletSpeed,
                color=(255, 255, 0),  # yellow player shots
            )
        )
        self.lastShotTime = currentTime
















    # ---------- ENEMY PATTERNS (Touhou-style helpers) ----------

    def shoot_aimed(self, x, y, target_x, target_y, speed=None, color=(0, 255, 255)):
        """Single bullet aimed at the target (e.g. the player)."""
        if speed is None:
            speed = self.bulletSpeed

        dx = target_x - x
        dy = target_y - y
        dist = math.hypot(dx, dy)
        if dist == 0:
            return  # avoid divide by zero

        vx = dx / dist * speed
        vy = dy / dist * speed
        self.bullets.append(Bullet(x, y, vx, vy, color=color))

    def shoot_radial(self, x, y, count=16, speed=None, color=(255, 120, 120)):
        """Perfect circle of bullets (classic Touhou 'flower' burst)."""
        if speed is None:
            speed = self.bulletSpeed

        for i in range(count):
            angle = 2 * math.pi * i / count
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.bullets.append(Bullet(x, y, vx, vy, color=color))

    def shoot_spread(self, x, y, base_angle, spread_angle, count=7,
                     speed=None, color=(255, 180, 80)):
        """Fan/spread of bullets around a base angle (e.g. wide cone)."""
        if speed is None:
            speed = self.bulletSpeed

        if count <= 1:
            angles = [base_angle]
        else:
            angles = [
                base_angle - spread_angle / 2 + spread_angle * i / (count - 1)
                for i in range(count)
            ]

        for angle in angles:
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.bullets.append(Bullet(x, y, vx, vy, color=color))

    def shoot_spiral(self, x, y, count=8, step=0.2, speed=None,
                     color=(200, 120, 255)):
        """Spiral: each call advances the angle, like rotating flower patterns."""
        if speed is None:
            speed = self.bulletSpeed

        for i in range(count):
            angle = self.spiral_angle + step * i
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.bullets.append(Bullet(x, y, vx, vy, color=color))

        # slowly rotate the spiral over time
        self.spiral_angle += step

    # ---------- UPDATE / DRAW ----------

    def updateBullets(self):
        for bullet in self.bullets:
            bullet.update()

        # Cull bullets that are far off-screen
        margin = 20
        self.bullets = [
            b for b in self.bullets
            if -margin <= b.x <= self.screenWidth + margin
            and -margin <= b.y <= self.screenHeight + margin
        ]

        #For custom bullets for Rumia

    def spawn_custom(self, x, y, vx, vy):
        bullet = EnemyBullet(x, y, vx, vy)
        self.bullets.append(bullet)
        return bullet


    def drawBullets(self, screen)   :
        for bullet in self.bullets:
            bullet.draw(screen)
