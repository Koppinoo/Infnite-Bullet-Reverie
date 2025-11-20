import pygame
from pygame.locals import *

pygame.init()
from bullet_system import BulletSystem
from enemy_system import EnemySystem

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
playerLives = 3
playerInvulnerable = False  # optional, can add later for brief invulnerability after hit


# --- Setup For Bullet System
isShooting = False
playerBullets = BulletSystem()  # bullets shot by the player
enemyBullets = BulletSystem()  # bullets shot by enemies

# --- Setup For Enemy System ---
enemySystem = EnemySystem(screenWidth, screenHeight)

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

    from collision_system import check_collision

    # --- Check collisions between player and enemy bullets ---
    for bullet in enemyBullets.bullets:
        if check_collision(playerX, playerY, playerSize, playerSize,
                           bullet.x, bullet.y, bullet.width, bullet.height):
            playerLives -= 1
            print(f"DEBUG: Player hit! Lives remaining: {playerLives}")
            enemyBullets.bullets.remove(bullet)



    # --- Check collisions between player and enemies ---
    for enemy in enemySystem.enemies:
        if check_collision(playerX, playerY, playerSize, playerSize, enemy.x, enemy.y, enemy.width, enemy.height):
            playerLives = 0  # instant death for testing
            print("DEBUG: Player collided with enemy!")

    # --- Lives Left ---
    if playerLives <= 0:
        print("GAME OVER")  # debug print
        running = False  # temporarily ends the game to indicate game over


    # --- Boundary checks ---
    playerX = max(0, min(screenWidth - playerSize, playerX))
    playerY = max(0, min(screenHeight - playerSize, playerY))

    # --- Shooting logic ---
    if isShooting:
        playerBullets.shoot(playerX, playerY, playerSize)

    playerBullets.updateBullets()

    # --- Draw everything ---
    screen.fill((0, 0, 0))
    playerBullets.drawBullets(screen)
    pygame.draw.rect(screen, (0, 255, 255), (playerX, playerY, playerSize, playerSize))

    # --- Debug text ---
    font = pygame.font.SysFont(None, 30)
    debugText = font.render(f"Z Pressed: {isShooting}", True, (255, 255, 255))
    screen.blit(debugText, (10, 10))



    # --- Drawing Enemies ---
    enemySystem.spawnEnemy()  # spawns new enemies periodically
    enemySystem.updateEnemies()  # moves enemies
    enemySystem.drawEnemies(screen)  # draws enemies

    # --- Drawing Lives ---
    font = pygame.font.SysFont(None, 30)
    livesText = font.render(f"Lives: {playerLives}", True, (255, 255, 255))
    screen.blit(livesText, (10, 40))

    # --- Update Enemies ---
    enemySystem.updateEnemies()

    # --- Drawing  Enemies ---
    enemySystem.drawEnemies(screen)

    # Check collisions: player bullets vs enemies
    for bullet in playerBullets.bullets[:]:  # copy to avoid iteration issues
        for enemy in enemySystem.enemies[:]:
            if check_collision(bullet.x, bullet.y, bullet.width, bullet.height,
                               enemy.x, enemy.y, enemy.width, enemy.height):
                enemy.health -= 1
                if enemy.health <= 0:
                    enemySystem.enemies.remove(enemy)
                playerBullets.bullets.remove(bullet)
                break  # bullet can only hit one enemy

    pygame.display.flip()
    clock.tick(60)

pygame.quit()