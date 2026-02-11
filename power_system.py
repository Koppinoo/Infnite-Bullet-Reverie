import pygame

class PowerItem:
    def __init__(self, x, y):

        # Initial spawn position
        self.x = x
        self.y = y

        # Arc movement
        self.vy = -4      # initial upward force
        self.gravity = 0.2

        self.width = 16
        self.height = 16

        self.collected = False

    def update(self):

        # Apply gravity
        self.vy += self.gravity
        self.y += self.vy

    def draw(self, screen):

        # TEMP: simple red circle (sprite later)
        pygame.draw.circle(
            screen,
            (255, 50, 50),
            (int(self.x), int(self.y)),
            6
        )


class ItemSystem:
    def __init__(self):
        self.items = []

    def spawn_power(self, x, y):
        self.items.append(PowerItem(x, y))

    def update(self):
        for item in self.items[:]:
            item.update()
            if item.y > 800:  # off screen
                self.items.remove(item)

    def draw(self, screen):
        for item in self.items:
            item.draw(screen)
