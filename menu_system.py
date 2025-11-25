import pygame

class MenuSystem:
    def __init__(self):
        self.state = "menu"  # can be: menu, controls, game

        # default controls
        self.controls = {
            "shoot": pygame.K_z,
            "left": pygame.K_LEFT,
            "right": pygame.K_RIGHT,
            "up": pygame.K_UP,
            "down": pygame.K_DOWN,
            "slow": pygame.K_LSHIFT
        }

        # For rebinding
        self.rebinding = None  # holds which action is being rebound

        self.font = pygame.font.SysFont(None, 50)
        self.smallFont = pygame.font.SysFont(None, 30)

    def draw_menu(self, screen):
        screen.fill((0, 0, 0))
        title = self.font.render("Infinite Bullet Reverie", True, (255, 255, 255))
        start = self.smallFont.render("Press ENTER to Start", True, (200, 200, 200))
        controls = self.smallFont.render("Press C for Controls", True, (200, 200, 200))

        screen.blit(title, (120, 150))
        screen.blit(start, (250, 300))
        screen.blit(controls, (250, 350))

    def draw_controls(self, screen):
        screen.fill((0, 0, 0))

        header = self.font.render("Controls", True, (255, 255, 255))
        screen.blit(header, (300, 80))

        y = 200
        for action, key in self.controls.items():
            text = self.smallFont.render(
                f"{action.capitalize()}: {pygame.key.name(key)}",
                True, (255, 255, 255)
            )
            screen.blit(text, (200, y))
            y += 40

        msg = self.smallFont.render("Press R to Rebind Controls | ESC to return", True, (200, 200, 200))
        screen.blit(msg, (150, 500))

        if self.rebinding:
            waiting = self.smallFont.render(f"Press a key for: {self.rebinding}", True, (255, 200, 200))
            screen.blit(waiting, (200, 550))

    def handle_menu_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.state = "game"
            if event.key == pygame.K_c:
                self.state = "controls"

    def handle_controls_input(self, event):
        if event.type == pygame.KEYDOWN:

            if self.rebinding:
                # Set new key
                self.controls[self.rebinding] = event.key
                self.rebinding = None
                return

            if event.key == pygame.K_ESCAPE:
                self.state = "menu"
            if event.key == pygame.K_r:
                # start rebinding process
                actions = list(self.controls.keys())
                self.rebinding = actions[0] if actions else None

            # Cycle through actions to rebind
            elif self.rebinding:
                actions = list(self.controls.keys())
                idx = actions.index(self.rebinding)
                if idx + 1 < len(actions):
                    self.rebinding = actions[idx + 1]
                else:
                    self.rebinding = None
