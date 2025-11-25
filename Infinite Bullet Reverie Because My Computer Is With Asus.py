# main.py
# Clean integrated main loop for Infinite Bullet Reverie
# Uses modular systems: bullet_system, enemy_system, menu_system, collision_system
# Author: (you) — personalised comments kept throughout for coursework clarity

import pygame
import sys
from pygame.locals import *

# Modular systems (must exist in the same folder)
from bullet_system import BulletSystem
from enemy_system import EnemySystem
from menu_system import MenuSystem
from collision_system import check_collision

# --- Pygame init ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Bullet Reverie")
clock = pygame.time.Clock()

# --- Systems ---
menu = MenuSystem()
playerBullets = BulletSystem(bulletSpeed=10, shootCooldown=150)   # player's bullets
enemyBullets = BulletSystem(bulletSpeed=6, shootCooldown=500)     # can be used for enemy fire later
enemySystem = EnemySystem(WIDTH, HEIGHT)

# --- Player state (resettable) ---
def reset_player_state():
    return {
        "x": WIDTH // 2,
        "y": HEIGHT // 2,
        "size": 32,
        "normalSpeed": 5,
        "focusSpeed": 2,
        "lives": 3,
        "invulnerable": False,
        "invulnTimer": 0
    }

player = reset_player_state()

# --- Fonts (create once) ---
title_font = pygame.font.SysFont(None, 64)
ui_font = pygame.font.SysFont(None, 28)

# --- Utility: restart entire game state ---
def restart_game():
    global player, playerBullets, enemyBullets, enemySystem
    player = reset_player_state()
    playerBullets = BulletSystem(bulletSpeed=10, shootCooldown=150)
    enemyBullets = BulletSystem(bulletSpeed=6, shootCooldown=500)
    enemySystem = EnemySystem(WIDTH, HEIGHT)
    menu.state = "game"

# --- Main loop ---
running = True
while running:
    # Process events first (menu may handle some events)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            break

        # Route events to menu when appropriate
        if menu.state == "menu":
            menu.handle_menu_input(event)
            continue
        elif menu.state == "controls":
            menu.handle_controls_input(event)
            continue
        elif menu.state == "gameover":
            # In gameover state, listen for restart (R) or quit (Q)
            if event.type == KEYDOWN:
                if event.key == pygame.K_r:
                    restart_game()
                elif event.key == pygame.K_q:
                    running = False
            continue

        # If playing, allow menu to receive some inputs (toggle)
        if menu.state == "game":
            # Allow escape to go back to menu
            if event.type == KEYDOWN and event.key == pygame.K_ESCAPE:
                menu.state = "menu"
                continue

    # If menu is active, draw menu and skip game update
    if menu.state == "menu":
        menu.draw_menu(screen)
        pygame.display.flip()
        clock.tick(60)
        continue
    if menu.state == "controls":
        menu.draw_controls(screen)
        pygame.display.flip()
        clock.tick(60)
        continue

    # --- GAME STATE UPDATES (menu.state == "game") ---

    # Use current controls mapping (they may be rebound in menu)
    controls = menu.controls
    keys = pygame.key.get_pressed()

    # Movement input (continuous)
    move_left = keys[controls["left"]]
    move_right = keys[controls["right"]]
    move_up = keys[controls["up"]]
    move_down = keys[controls["down"]]
    is_focus = keys[controls["slow"]]
    is_shooting = keys[controls["shoot"]]

    # Movement logic with diagonal normalisation
    speed = player["focusSpeed"] if is_focus else player["normalSpeed"]
    moveX = 0
    moveY = 0
    if move_left:
        moveX -= 1
    if move_right:
        moveX += 1
    if move_up:
        moveY -= 1
    if move_down:
        moveY += 1
    if moveX != 0 and moveY != 0:
        # normalize so diagonal speed equals straight speed
        moveX *= 0.7071
        moveY *= 0.7071
    player["x"] += moveX * speed
    player["y"] += moveY * speed

    # Boundary clamp
    player["x"] = max(0, min(WIDTH - player["size"], player["x"]))
    player["y"] = max(0, min(HEIGHT - player["size"], player["y"]))

    # Shooting (player)
    if is_shooting:
        playerBullets.shoot(player["x"], player["y"], player["size"])
    playerBullets.updateBullets()

    # Enemy spawn/update/draw calls
    enemySystem.spawnEnemy()
    enemySystem.updateEnemies()

    # Update enemy bullets (if you use enemyBullets later)
    enemyBullets.updateBullets()

    # --- COLLISIONS ---

    # 1) Enemy bullets hitting player
    for eb in enemyBullets.bullets[:]:
        if check_collision(player["x"], player["y"], player["size"], player["size"],
                           eb.x, eb.y, eb.width, eb.height):
            # only apply if not invulnerable
            if not player["invulnerable"]:
                player["lives"] -= 1
                player["invulnerable"] = True
                player["invulnTimer"] = pygame.time.get_ticks()
                # remove bullet that hit
                try:
                    enemyBullets.bullets.remove(eb)
                except ValueError:
                    pass

    # invulnerability timeout (300ms)
    if player["invulnerable"]:
        if pygame.time.get_ticks() - player["invulnTimer"] > 300:
            player["invulnerable"] = False

    # 2) Player bullets hitting enemies
    # iterate copies to allow removal during loops
    for pb in playerBullets.bullets[:]:
        for enemy in enemySystem.enemies[:]:
            if check_collision(pb.x, pb.y, pb.width, pb.height,
                               enemy.x, enemy.y, enemy.width, enemy.height):
                enemy.health -= 1
                # remove the bullet that hit
                try:
                    playerBullets.bullets.remove(pb)
                except ValueError:
                    pass
                # if enemy died, remove it
                if enemy.health <= 0:
                    try:
                        enemySystem.enemies.remove(enemy)
                    except ValueError:
                        pass
                break  # bullet can only hit one enemy

    # 3) Enemy colliding with player (instant death for testing)
    for enemy in enemySystem.enemies[:]:
        if check_collision(player["x"], player["y"], player["size"], player["size"],
                           enemy.x, enemy.y, enemy.width, enemy.height):
            player["lives"] = 0
            break

    # Check game over
    if player["lives"] <= 0:
        menu.state = "gameover"

    # --- DRAW ---
    screen.fill((10, 10, 30))  # dark background

    # Draw bullets and enemies then player (simple layering)
    playerBullets.drawBullets(screen)
    enemySystem.drawEnemies(screen)
    enemyBullets.drawBullets(screen)

    # Player draw - flash while invulnerable
    player_color = (0, 255, 255) if not player["invulnerable"] or (pygame.time.get_ticks() % 300 < 150) else (100, 100, 100)
    pygame.draw.rect(screen, player_color, (player["x"], player["y"], player["size"], player["size"]))

    # HUD
    score_text = ui_font.render(f"Lives: {player['lives']}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    ztext = ui_font.render(f"Shoot: {pygame.key.name(controls['shoot'])}", True, (200, 200, 200))
    screen.blit(ztext, (10, 40))

    # If gameover show overlay
    if menu.state == "gameover":
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        go_text = title_font.render("GAME OVER", True, (220, 50, 50))
        info = ui_font.render("Press R to restart or Q to quit", True, (255, 255, 255))
        screen.blit(go_text, (WIDTH//2 - go_text.get_width()//2, HEIGHT//2 - 50))
        screen.blit(info, (WIDTH//2 - info.get_width()//2, HEIGHT//2 + 20))

    pygame.display.flip()
    clock.tick(60)

# Clean exit
pygame.quit()
sys.exit()
