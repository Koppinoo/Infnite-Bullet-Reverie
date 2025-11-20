import pygame
from pygame.locals import *

pygame.init()
from bullet_system import BulletSystem

# --- Window setup ---
screenWidth = 800
screenHeight = 600
screen = pygame.display.set_mode((screenWidth, screenHeight))
pygame.display.set_caption("InfiniteBulletReverie")

clock = pygame.time.Clock()

# --- Player setup ---
playerX = screenWidth // 2
playerY = screenHeight // 2
playerSpeed = 5
slowSpeed = 2
playerSize = 32  # for boundary checks

# --- Setup For Bullet System
bulletSystem = BulletSystem()
isShooting = False

# --- Input handler variables ---
moveLeft = moveRight = moveUp = moveDown = False
isSlow = False
running = True

# --- Main loop ---
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        elif event.type == KEYDOWN:
            if event.key == K_LEFT:
                moveLeft = True
            if event.key == K_RIGHT:
                moveRight = True
            if event.key == K_UP:
                moveUp = True
            if event.key == K_DOWN:
                moveDown = True
            if event.key == K_LSHIFT:
                isSlow = True
            if event.key == K_z:
                isShooting = True
                print("DEBUG: Z key pressed")

        elif event.type == KEYUP:
            if event.key == K_LEFT:
                moveLeft = False
            if event.key == K_RIGHT:
                moveRight = False
            if event.key == K_UP:
                moveUp = False
            if event.key == K_DOWN:
                moveDown = False
            if event.key == K_LSHIFT:
                isSlow = False
            if event.key == K_z:
                isShooting = False
                print("DEBUG: Z key released")

    # --- Movement handling ---
    currentSpeed = slowSpeed if isSlow else playerSpeed
    moveX = 0
    moveY = 0
    if moveLeft:
        moveX -= 1
    if moveRight:
        moveX += 1
    if moveUp:
        moveY -= 1
    if moveDown:
        moveY += 1
    if moveX != 0 and moveY != 0:
        moveX *= 0.7071
        moveY *= 0.7071
    playerX += moveX * currentSpeed
    playerY += moveY * currentSpeed

    # --- Boundary checks ---
    playerX = max(0, min(screenWidth - playerSize, playerX))
    playerY = max(0, min(screenHeight - playerSize, playerY))

    # --- Shooting logic ---
    if isShooting:
        bulletSystem.shoot(playerX, playerY, playerSize)

    bulletSystem.updateBullets()

    # --- Draw everything ---
    screen.fill((0, 0, 0))
    bulletSystem.drawBullets(screen)
    pygame.draw.rect(screen, (0, 255, 255), (playerX, playerY, playerSize, playerSize))

    # --- Debug text ---
    font = pygame.font.SysFont(None, 30)
    debugText = font.render(f"Z Pressed: {isShooting}", True, (255, 255, 255))
    screen.blit(debugText, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()