import pygame

class WaveSystem:
    def __init__(self):
        self.currentWave = 1

        self.enemiesPerWave = 6
        self.enemiesSpawned = 0

        self.spawnDelay = 400  # ms between enemy spawns
        self.lastSpawnTime = 0

        self.waveCooldown = False
        self.waveCooldownStart = 0
        self.WAVE_COOLDOWN_TIME = 2000  # ms between waves

        self.waveActive = True

    def update(self, enemySystem, gamePaused):
        if gamePaused:
            return

        currentTime = pygame.time.get_ticks()

        # --- Spawn enemies in controlled bursts ---
        if self.waveActive:
            if self.enemiesSpawned < self.enemiesPerWave:
                if currentTime - self.lastSpawnTime >= self.spawnDelay:
                    enemySystem.spawnEnemy()
                    self.enemiesSpawned += 1
                    self.lastSpawnTime = currentTime
            else:
                self.waveActive = False

        # --- Check if wave is cleared ---
        if not self.waveActive and len(enemySystem.enemies) == 0:
            if not self.waveCooldown:
                self.waveCooldown = True
                self.waveCooldownStart = currentTime

        # --- Start next wave ---
        if self.waveCooldown:
            if currentTime - self.waveCooldownStart >= self.WAVE_COOLDOWN_TIME:
                self.start_next_wave(enemySystem)

    def start_next_wave(self, enemySystem):
        self.currentWave += 1

        # Touhou-style scaling
        self.enemiesPerWave += 2
        self.spawnDelay = max(120, self.spawnDelay - 30)

        enemySystem.enemySpeed += 0.25

        self.enemiesSpawned = 0
        self.waveActive = True
        self.waveCooldown = False
