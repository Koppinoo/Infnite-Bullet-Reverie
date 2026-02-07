
import pygame
import random

class WaveSystem:
    """
    Touhou-style phase + generator system.

    - Phase lasts PHASE_FRAMES (default 1800 frames = 30s at 60 FPS)
    - Within each phase, 'generators' spawn different enemy groups at set deltas
    - This matches Touhou's EnemyManager.generateEnemy() style much more closely
    """
    def __init__(self, field_x: int, field_width: int, field_y: int = 0, fps: int = 60):
        self.field_x = field_x
        self.field_width = field_width
        self.field_y = field_y
        self.fps = fps

        # Timekeeping (frames, like Touhou's elapsedFrame)
        self.elapsedFrame = 0

        # Phase system (30 seconds each)
        self.phase = 0
        self.PHASE_FRAMES = 60 * 30  # 1800 frames

        # Blue fairy horizontal sweep (Touhou-style)
        self.blueX = self.field_x
        self.directionBlueX = 1

        # Default deltas (spawn intervals)
        self.defaultDeltaBlue = 30
        self.defaultDeltaPink = 120

        # Current countdowns
        self.deltaBlue = self.defaultDeltaBlue
        self.deltaPink = self.defaultDeltaPink

        # A simple "playfield top" spawn line
        self.spawnY = self.field_y - 40  # spawn just above visible area

    def _advance_phase_if_needed(self):
        if self.elapsedFrame > 0 and self.elapsedFrame % self.PHASE_FRAMES == 0:
            self.phase += 1

    def _update_blue_sweep(self):
        # Move the sweep position within the playfield bounds
        field_x2 = self.field_x + self.field_width - 32
        self.blueX += self.directionBlueX * 3  # sweep speed
        if self.blueX >= field_x2:
            self.blueX = field_x2
            self.directionBlueX = -1
        elif self.blueX <= self.field_x:
            self.blueX = self.field_x
            self.directionBlueX = 1

    def _choose_random_x(self):
        return random.randint(self.field_x, self.field_x + self.field_width - 32)

    def generateBlueFairy(self, enemySystem):
        self.deltaBlue -= 1
        self._update_blue_sweep()
        if self.deltaBlue <= 0:
            self.deltaBlue = self.defaultDeltaBlue
            enemySystem.spawn(
                enemy_type="BlueFairy",
                x=self.blueX,
                y=self.spawnY,
                direction=(0, 1),
                velocity=(self.phase + 1) * 1.0
            )

    def generateHardBlueFairy(self, enemySystem):
        # spawn a pair
        self.deltaBlue -= 1
        self._update_blue_sweep()
        if self.deltaBlue <= 0:
            self.deltaBlue = self.defaultDeltaBlue
            x = self.blueX
            y = self.spawnY
            v = (self.phase + 1) * 1.0
            enemySystem.spawn("BlueFairy", x, y, direction=(0, 1), velocity=v)
            enemySystem.spawn("BlueFairy", x + 20, y, direction=(0, 1), velocity=v)

    def generateExtraBlueFairy(self, enemySystem):
        # spawn four (two on each side)
        self.deltaBlue -= 1
        self._update_blue_sweep()
        if self.deltaBlue <= 0:
            self.deltaBlue = self.defaultDeltaBlue
            x = self.blueX
            y = self.spawnY
            v = (self.phase + 1) * 1.0

            enemySystem.spawn("BlueFairy", x, y, direction=(0, 1), velocity=v)
            enemySystem.spawn("BlueFairy", x + 20, y, direction=(0, 1), velocity=v)

            # mirrored side
            mirror_x = (self.field_x + self.field_width - 32) - x
            enemySystem.spawn("BlueFairy", mirror_x, y, direction=(0, 1), velocity=v)
            enemySystem.spawn("BlueFairy", mirror_x + 20, y, direction=(0, 1), velocity=v)

    def generatePinkFairy(self, enemySystem):
        self.deltaPink -= 1
        if self.deltaPink <= 0:
            self.deltaPink = self.defaultDeltaPink
            enemySystem.spawn(
                enemy_type="PinkFairy",
                x=self._choose_random_x(),
                y=self.spawnY,
                direction=(0, 1),
                velocity=1.0
            )

    def generateGoodPinkFairy(self, enemySystem):
        self.deltaPink -= 1
        if self.deltaPink <= 0:
            self.deltaPink = self.defaultDeltaPink
            enemySystem.spawn(
                enemy_type="PinkFairyGood",
                x=self._choose_random_x(),
                y=self.spawnY,
                direction=(0, 1),
                velocity=1.0
            )

    def update(self, enemySystem, gamePaused: bool):
        """
        Call once per frame.
        """
        if gamePaused:
            return

        self.elapsedFrame += 1
        self._advance_phase_if_needed()

        # Phase -> spawn tuning (mirrors your Touhou table)
        if self.phase == 0:
            self.defaultDeltaBlue = 30
            self.defaultDeltaPink = 120
            self.generateBlueFairy(enemySystem)
            self.generatePinkFairy(enemySystem)

        elif self.phase == 1:
            self.defaultDeltaBlue = 15
            self.defaultDeltaPink = 90
            self.generateBlueFairy(enemySystem)
            self.generatePinkFairy(enemySystem)

        elif self.phase == 2:
            self.defaultDeltaBlue = 10
            self.defaultDeltaPink = 60
            self.generateHardBlueFairy(enemySystem)
            self.generatePinkFairy(enemySystem)

        elif self.phase == 3:
            self.defaultDeltaBlue = 10
            self.defaultDeltaPink = 75
            self.generateExtraBlueFairy(enemySystem)
            self.generateGoodPinkFairy(enemySystem)

        else:
            # Boss phase later (keep spawning stopped for now)
            pass

    def get_phase(self) -> int:
        return self.phase

    def get_elapsed_frame(self) -> int:
        return self.elapsedFrame
