import pygame
class WaveSystem:
    def __init__(self):

        # Wave Counter
        self.currentWave = 1

        #Enemies Per Wave
        self.enemiesPerWave = 6
        self.enemiesSpawned = 0

        self.spawnDelay = 400  # ms between enemy spawns
        self.lastSpawnTime = 0

        self.waveCooldown = False
        self.waveCooldownStart = 0
        self.WAVE_COOLDOWN_TIME = 2000  # ms between waves

        self.waveActive = True

        self.groupIndex = 0
        self.groupsPerPhase = 3  # Touhou-style: multiple groups per phase
        self.groupCooldown = False
        self.groupCooldownStart = 0
        GROUP_COOLDOWN_TIME = 1200  # ms between groups

        #Phase Timing
        self.phase = 0
        self.phaseStartTime = pygame.time.get_ticks()
        self.PHASE_DURATION = 30000  # 30 seconds

    def update(self, enemySystem, gamePaused):
            if gamePaused:
                return

            currentTime = pygame.time.get_ticks()

            # ---------------- PHASE TIMER ----------------
            if currentTime - self.phaseStartTime >= self.PHASE_DURATION:
                self.phase += 1
                self.phaseStartTime = currentTime
                self.groupIndex = 0
                self.waveActive = True
                self.enemiesSpawned = 0
                self.groupCooldown = False

            # ---------------- SPAWNING GROUP ----------------
            if self.waveActive:
                if currentTime - self.lastSpawnTime >= self.spawnDelay:
                    if self.enemiesSpawned < self.enemiesPerWave:

                        if self.phase == 0:
                            enemyType = "BlueFairy"
                        elif self.phase == 1:
                            enemyType = "PinkFairy"
                        else:
                            enemyType = "PinkFairyGood"

                        lane_targets = [90, 150, 210]
                        targetY = lane_targets[self.enemiesSpawned % len(lane_targets)]

                        enemySystem.spawnEnemy(
                            enemy_type=enemyType,
                            targetY=targetY
                        )

                        self.enemiesSpawned += 1
                        self.lastSpawnTime = currentTime
                    else:
                        # Group finished spawning
                        self.waveActive = False

            # ---------------- GROUP COMPLETION ----------------
            if not self.waveActive and len(enemySystem.enemies) == 0:
                if not self.groupCooldown:
                    self.groupCooldown = True
                    self.groupCooldownStart = currentTime

            # ---------------- START NEXT GROUP ----------------
            if self.groupCooldown:
                if currentTime - self.groupCooldownStart >= 1200:
                    self.groupIndex += 1
                    self.groupCooldown = False

                    if self.groupIndex < self.groupsPerPhase:
                        # Start next group in same phase
                        self.enemiesSpawned = 0
                        self.enemiesPerWave = 4 + self.groupIndex * 2
                        self.waveActive = True
                    else:
                        # Phase continues but no more groups
                        self.waveActive = False
