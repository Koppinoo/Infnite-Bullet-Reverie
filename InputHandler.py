import pygame

class InputHandler:
    def __init__(self):
        # Movement variables
        self.moveLeft = False
        self.moveRight = False
        self.moveUp = False
        self.moveDown = False

        # Action variables
        self.shooting = False
        self.bombing = False
        self.focus = False
        self.pause = False

    def update(self):
        """Update input variables based on key states."""
        keys = pygame.key.get_pressed()

        # Movement
        self.moveLeft = keys[pygame.K_LEFT]
        self.moveRight = keys[pygame.K_RIGHT]
        self.moveUp = keys[pygame.K_UP]
        self.moveDown = keys[pygame.K_DOWN]

        # Actions
        self.shooting = keys[pygame.K_z]
        self.bombing = keys[pygame.K_x]
        self.focus = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        self.pause = keys[pygame.K_ESCAPE]
