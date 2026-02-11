# main.py
import pygame
import sys
from pygame.locals import *

# Modular systems (must exist in the same folder)
from bullet_system import BulletSystem
from enemy_system import EnemySystem
from menu_system import MenuSystem
from collision_system import circle_rect_collision, HITBOX_RADIUS, check_collision
from WaveSystem import WaveSystem
from boss_system import Rumia

bossSystem = Rumia(screen_width=800)

waveSystem = WaveSystem()



# --- Pygame init ---
pygame.init()
WIDTH, HEIGHT = 800, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Infinite Bullet Reverie")
clock = pygame.time.Clock()

# --- Systems ---
menu = MenuSystem()
playerBullets = BulletSystem(bulletSpeed=10, shootCooldown=150, screenWidth=WIDTH, screenHeight=HEIGHT)
enemyBullets  = BulletSystem(bulletSpeed=6,  shootCooldown=500, screenWidth=WIDTH, screenHeight=HEIGHT)
enemySystem = EnemySystem(WIDTH, HEIGHT)

# --- Player hitbox ---
HITBOX_RADIUS = 4  # Small visual hitbox for precision dodging



# --- Paused State ---
gamePaused = False

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
        "invulnTimer": 0,
        "powerValue": 1,
        "powerLevel": 1,
        "fireCooldown": 0,
        "fireRate": 6,
        "chaseCooldown": 0,
        "chaseRate": 30,  # will change by power level

    }

player = reset_player_state()

# --- Fonts (create once) ---
title_font = pygame.font.SysFont(None, 64)
ui_font = pygame.font.SysFont(None, 28)

def update_power_level(player):
    pv = player["powerValue"]

    if pv >= 60:
        player["powerLevel"] = 5
    elif pv >= 35:
        player["powerLevel"] = 4
    elif pv >= 20:
        player["powerLevel"] = 3
    elif pv >= 10:
        player["powerLevel"] = 2
    else:
        player["powerLevel"] = 1

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


            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    gamePaused = not gamePaused

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

    if not gamePaused:
        bossSystem.update(enemyBullets,player)

        waveSystem.update(enemySystem, gamePaused,bossSystem)

        # Movement input (continuous)
        move_left = keys[controls["left"]]
        move_right = keys[controls["right"]]
        move_up = keys[controls["up"]]
        move_down = keys[controls["down"]]
        is_focus = keys[controls["slow"]]
        is_shooting = keys[controls["shoot"]]

        # --- Fire cooldown tick-down ---
        if player["fireCooldown"] > 0:
            player["fireCooldown"] -= 1

        # --- Chase cooldown tick-down ---
        if player["chaseCooldown"] > 0:
            player["chaseCooldown"] -= 1

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
        if is_shooting and player["fireCooldown"] == 0:

            px = player["x"] + player["size"] // 2
            py = player["y"]
            size = player["size"]

            if player["powerLevel"] == 1:
                # Single forward shot
                playerBullets.shoot(player["x"], player["y"], player["size"])

            elif player["powerLevel"] == 2:
                # Single + slight side shot
                playerBullets.shoot(player["x"], player["y"], player["size"])
                playerBullets.spawn_custom(px - 8, py, 0, -8)

            elif player["powerLevel"] == 3:
                # Dual parallel
                playerBullets.spawn_custom(px - 6, py, 0, -8)
                playerBullets.spawn_custom(px + 6, py, 0, -8)

            elif player["powerLevel"] == 4:
                # 3-way spread
                playerBullets.spawn_custom(px, py, 0, -8)
                playerBullets.spawn_custom(px, py, -2, -8)
                playerBullets.spawn_custom(px, py, 2, -8)

            elif player["powerLevel"] >= 5:
                # 5-way spread
                for angle in [-4, -2, 0, 2, 4]:
                    playerBullets.spawn_custom(px, py, angle, -8)

            player["fireCooldown"] = player["fireRate"]

        # Enemy spawn/update/draw calls
        enemySystem.updateEnemies(
            enemyBullets,
            player["x"],
            player["y"],
            player["size"],

        )
        bossSystem.update(enemyBullets,player)
        playerBullets.updateBullets()

        enemyBullets.updateBullets()

        # --- COLLISIONS ---

        # 1) Enemy bullets hitting player
        for eb in enemyBullets.bullets[:]:
            # Calculate player hitbox centre
            hitbox_x = player["x"] + player["size"] // 2
            hitbox_y = player["y"] + player["size"] // 2

            # Use circular hitbox collision,
            if circle_rect_collision(
                    hitbox_x,
                    hitbox_y,
                    HITBOX_RADIUS,
                    eb.x,
                    eb.y,
                    eb.width,
                    eb.height
            ):

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
                    print("HIT BY ENEMY BULLET")

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
                            player["powerValue"] += 2  # Gain 2 power per kill
                            update_power_level(player)
                            enemySystem.enemies.remove(enemy)
                        except ValueError:
                            pass
                    break  # bullet can only hit one enemy

            # 2B) Player bullets hitting Boss (Rumia)
            if bossSystem.spawned and not bossSystem.dead:
                for pb in playerBullets.bullets[:]:
                    if check_collision(
                            pb.x, pb.y, pb.width, pb.height,
                            bossSystem.x - bossSystem.width // 2,
                            bossSystem.y,
                            bossSystem.width,
                            bossSystem.height
                    ):
                        bossSystem.hp -= 1  # Reduce boss HP

                        try:
                            playerBullets.bullets.remove(pb)
                        except ValueError:
                            pass

                        # Check if boss dies
                        if bossSystem.hp <= 0:
                            bossSystem.dead = True

        # 3) Enemy colliding with player (instant death for testing)
        for enemy in enemySystem.enemies[:]:
            # Calculate player hitbox centre
            hitbox_x = player["x"] + player["size"] // 2
            hitbox_y = player["y"] + player["size"] // 2

            # Use circular hitbox collision for enemy body
            if circle_rect_collision(
                    hitbox_x,
                    hitbox_y,
                    HITBOX_RADIUS,
                    enemy.x,
                    enemy.y,
                    enemy.width,
                    enemy.height

            ):
                player["lives"] = 0
                print("HIT BY ENEMY BODY ")
                break
        # 3B) Player colliding with Boss body
        if bossSystem.spawned and not bossSystem.dead:

            hitbox_x = player["x"] + player["size"] // 2
            hitbox_y = player["y"] + player["size"] // 2

            if circle_rect_collision(
                    hitbox_x,
                    hitbox_y,
                    HITBOX_RADIUS,
                    bossSystem.x - bossSystem.width // 2,
                    bossSystem.y,
                    bossSystem.width,
                    bossSystem.height
            ):
                if not player["invulnerable"]:
                    player["lives"] -= 1
                    player["invulnerable"] = True
                    player["invulnTimer"] = pygame.time.get_ticks()

        # Check game over
        if player["lives"] <= 0:
            menu.state = "gameover"

        # --- DRAW ---
        screen.fill((10, 10, 30))  # dark background

        # Draw bullets and enemies then player (simple layering)
        playerBullets.drawBullets(screen)
        enemySystem.drawEnemies(screen)
        enemyBullets.drawBullets(screen)

        #bossDrawing
        if bossSystem.spawned and not bossSystem.dead:
            bossSystem.draw(screen)

        # Player draw - flash while invulnerable
        player_color = (0, 255, 255) if not player["invulnerable"] or (pygame.time.get_ticks() % 300 < 150) else (100, 100, 100)
        pygame.draw.rect(screen, player_color, (player["x"], player["y"], player["size"], player["size"]))



    # Draw visible hitbox only when in focus mode (Touhou-style)
    if is_focus:
        hitbox_x = player["x"] + player["size"] // 2
        hitbox_y = player["y"] + player["size"] // 2

        pygame.draw.circle(
            screen,
            (255, 255, 255),  # white for high contrast
            (hitbox_x, hitbox_y),
            HITBOX_RADIUS,
            1  # outline only
        )

    # I draw a small visual hitbox when the player is in focus mode.
    # This represents the true collision area of the player and is intentionally
    # smaller than the player sprite to allow precise dodging.
    # The hitbox is only visible in focus mode to reduce screen clutter,



    # HUD
    score_text = ui_font.render(f"Lives: {player['lives']}", True, (255, 255, 255))
    power_text = ui_font.render(
        f"Power: {player['powerValue']} (Lv {player['powerLevel']})",
        True,
        (255, 255, 0)
    )
    screen.blit(power_text, (10, 70))
    screen.blit(score_text, (10, 10))
    ztext = ui_font.render(f"Shoot: {pygame.key.name(controls['shoot'])}", True, (200, 200, 200))
    screen.blit(ztext, (10, 40))


    # I implemented a pause system that freezes all gameplay updates when activated.
    # This prevents unfair deaths, allows players to take breaks, and improves accessibility.
    # This directly supports Success Criterion 13.

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

    if gamePaused:
        pause_font = pygame.font.Font(None, 72)
        pause_text = pause_font.render("PAUSED", True, (255, 255, 255))
        screen.blit(
            pause_text,
            (
                screen.get_width() // 2 - pause_text.get_width() // 2,
                screen.get_height() // 2 - pause_text.get_height() // 2
            )
        )

    pygame.display.flip()
    clock.tick(60)


# Clean exit
pygame.quit()
sys.exit()




