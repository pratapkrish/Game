"""Ram's Mario: a single-file, asset-free Pygame platformer."""
import math
import random
import sys
import pygame

WIDTH, HEIGHT = 800, 600
FPS = 60
TILE = 48
WORLD_WIDTH = 4608
GROUND_Y = 520
GRAVITY = 0.65
MAX_FALL = 14
SKY = (112, 198, 250)


def draw_text(surface, message, size, color, center, shadow=True):
    font = pygame.font.SysFont("consolas", size, bold=True)
    image = font.render(message, True, color)
    rect = image.get_rect(center=center)
    if shadow:
        dark = font.render(message, True, (33, 50, 75))
        surface.blit(dark, rect.move(2, 3))
    surface.blit(image, rect)


class Camera:
    def __init__(self):
        self.x = 0

    def update(self, player):
        target = player.rect.centerx - WIDTH * 0.38
        self.x = max(0, min(WORLD_WIDTH - WIDTH, int(target)))

    def screen(self, rect):
        return rect.move(-self.x, 0)


class Platform:
    def __init__(self, x, y, w=TILE, h=TILE, kind="ground"):
        self.rect = pygame.Rect(x, y, w, h)
        self.kind = kind

    def draw(self, screen, camera):
        r = camera.screen(self.rect)
        if r.right < 0 or r.left > WIDTH:
            return
        if self.kind == "pipe":
            pygame.draw.rect(screen, (21, 120, 54), r, border_radius=5)
            pygame.draw.rect(screen, (62, 209, 94), (r.x + 7, r.y + 5, 10, r.h - 9))
            pygame.draw.rect(screen, (9, 80, 39), (r.right - 12, r.y + 5, 8, r.h - 9))
            lip = pygame.Rect(r.x - 8, r.y, r.w + 16, 18)
            pygame.draw.rect(screen, (24, 151, 58), lip, border_radius=3)
            pygame.draw.rect(screen, (117, 240, 111), (lip.x + 5, lip.y + 3, lip.w - 10, 5))
            pygame.draw.rect(screen, (8, 82, 39), lip, 3, border_radius=3)
        elif self.kind == "brick":
            pygame.draw.rect(screen, (171, 83, 44), r)
            pygame.draw.rect(screen, (97, 45, 38), r, 3)
            pygame.draw.line(screen, (238, 153, 90), (r.x + 3, r.y + 4), (r.right - 4, r.y + 4), 3)
            pygame.draw.line(screen, (96, 48, 40), (r.x, r.y + r.h // 2), (r.right, r.y + r.h // 2), 3)
            pygame.draw.line(screen, (96, 48, 40), (r.centerx, r.y), (r.centerx, r.centery), 3)
            pygame.draw.line(screen, (96, 48, 40), (r.x + 12, r.centery), (r.x + 12, r.bottom), 3)
        else:
            pygame.draw.rect(screen, (142, 83, 47), r)
            pygame.draw.rect(screen, (81, 51, 44), r, 2)
            pygame.draw.rect(screen, (75, 190, 69), (r.x, r.y, r.w, 11))
            pygame.draw.rect(screen, (139, 220, 72), (r.x + 2, r.y + 2, r.w - 4, 4))
            for dx, dy in ((12, 24), (34, 40), (32, 18)):
                pygame.draw.circle(screen, (110, 67, 42), (r.x + dx, r.y + dy), 3)


class QuestionBlock:
    def __init__(self, x, y, reward="coin"):
        self.rect = pygame.Rect(x, y, TILE, TILE)
        self.reward = reward
        self.used = False
        self.bump = 0

    def hit(self, game):
        if self.used:
            return
        self.used = True
        self.bump = 12
        if self.reward == "mushroom":
            game.powerups.append(PowerUp(self.rect.centerx - 16, self.rect.top - 33))
        else:
            game.coins.append(Coin(self.rect.centerx, self.rect.y - 24, spawned=True))

    def update(self):
        if self.bump > 0:
            self.bump -= 1

    def draw(self, screen, camera):
        offset = -int(6 * math.sin(math.pi * self.bump / 12)) if self.bump else 0
        r = camera.screen(self.rect).move(0, offset)
        if r.right < 0 or r.left > WIDTH:
            return
        pygame.draw.rect(screen, (143, 102, 66) if self.used else (249, 172, 37), r, border_radius=4)
        pygame.draw.rect(screen, (111, 69, 41) if self.used else (160, 90, 24), r, 4, border_radius=4)
        for dx in (7, 40):
            for dy in (7, 40):
                pygame.draw.circle(screen, (255, 225, 135) if not self.used else (93, 64, 49), (r.x + dx, r.y + dy), 2)
        if not self.used:
            draw_text(screen, "?", 34, (255, 248, 201), r.center, shadow=False)


class Coin:
    def __init__(self, x, y, spawned=False):
        self.x, self.y = x, y
        self.phase = random.random() * math.tau
        self.rect = pygame.Rect(x - 12, y - 14, 24, 28)
        self.spawned = spawned

    def update(self):
        self.phase += 0.12

    def draw(self, screen, camera):
        x = int(self.x - camera.x)
        if not -20 < x < WIDTH + 20:
            return
        y = int(self.y + 3 * math.sin(self.phase))
        w = max(4, int(12 * abs(math.cos(self.phase))))
        pygame.draw.ellipse(screen, (155, 100, 18), (x - w - 2, y - 15, 2 * w + 4, 30))
        pygame.draw.ellipse(screen, (255, 211, 39), (x - w, y - 14, 2 * w, 27))
        if w > 6:
            pygame.draw.ellipse(screen, (255, 244, 125), (x - w + 4, y - 10, 2 * w - 8, 19), 2)


class PowerUp:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.vx, self.vy = 2.0, 0
        self.alive = True

    def update(self, solids):
        self.rect.x += round(self.vx)
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vx > 0:
                    self.rect.right = solid.rect.left
                else:
                    self.rect.left = solid.rect.right
                self.vx *= -1
        self.vy = min(MAX_FALL, self.vy + GRAVITY)
        self.rect.y += round(self.vy)
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vy > 0:
                    self.rect.bottom = solid.rect.top
                elif self.vy < 0:
                    self.rect.top = solid.rect.bottom
                self.vy = 0
        if self.rect.top > HEIGHT + 150:
            self.alive = False

    def draw(self, screen, camera):
        r = camera.screen(self.rect)
        pygame.draw.rect(screen, (251, 233, 194), (r.x + 6, r.y + 16, 20, 16), border_radius=5)
        pygame.draw.ellipse(screen, (218, 55, 48), (r.x, r.y + 2, 32, 22))
        for px, py in ((9, 9), (23, 9), (16, 17)):
            pygame.draw.circle(screen, (255, 242, 218), (r.x + px, r.y + py), 4)
        for px in (12, 21):
            pygame.draw.circle(screen, (37, 46, 46), (r.x + px, r.y + 24), 2)


class Enemy:
    def __init__(self, x, surface_y):
        self.rect = pygame.Rect(x, surface_y - 32, 34, 32)
        self.vx = -1.25
        self.vy = 0
        self.alive = True
        self.squash = 0

    def update(self, solids, enemies):
        if not self.alive:
            self.squash -= 1
            return
        self.rect.x += round(self.vx)
        blocked = False
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vx > 0:
                    self.rect.right = solid.rect.left
                else:
                    self.rect.left = solid.rect.right
                blocked = True
        for other in enemies:
            if other is not self and other.alive and self.rect.colliderect(other.rect):
                if self.vx > 0:
                    self.rect.right = other.rect.left
                else:
                    self.rect.left = other.rect.right
                blocked = True
        self.vy = min(MAX_FALL, self.vy + GRAVITY)
        self.rect.y += round(self.vy)
        grounded = False
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vy >= 0:
                    self.rect.bottom = solid.rect.top
                    grounded = True
                else:
                    self.rect.top = solid.rect.bottom
                self.vy = 0
        # Turn at the edge rather than walking into a pit.
        probe_x = self.rect.right + 4 if self.vx > 0 else self.rect.left - 4
        probe = pygame.Rect(probe_x, self.rect.bottom + 2, 4, 6)
        if blocked or (grounded and not any(probe.colliderect(s.rect) for s in solids)):
            self.vx *= -1

    def draw(self, screen, camera):
        r = camera.screen(self.rect)
        if not self.alive:
            if self.squash > 0:
                pygame.draw.ellipse(screen, (125, 61, 33), (r.x, r.bottom - 11, r.w, 11))
            return
        pygame.draw.ellipse(screen, (139, 77, 40), (r.x, r.y, 34, 29))
        pygame.draw.rect(screen, (105, 54, 37), (r.x + 3, r.y + 21, 28, 10), border_radius=4)
        for dx in (10, 23):
            pygame.draw.ellipse(screen, (247, 236, 214), (r.x + dx - 4, r.y + 10, 8, 12))
            pygame.draw.circle(screen, (38, 31, 28), (r.x + dx, r.y + 16), 2)
        pygame.draw.rect(screen, (48, 36, 33), (r.x - 1, r.bottom - 7, 15, 7))
        pygame.draw.rect(screen, (48, 36, 33), (r.right - 14, r.bottom - 7, 15, 7))


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 38)
        self.x, self.y = float(x), float(y)
        self.vx = self.vy = 0.0
        self.grounded = False
        self.big = False
        self.invincible = 0
        self.facing = 1
        self.jump_was_held = False

    def grow(self, solids):
        if self.big:
            return
        taller = pygame.Rect(self.rect.x, self.rect.bottom - 58, 30, 58)
        if not any(taller.colliderect(s.rect) for s in solids):
            self.rect = taller
            self.y = float(self.rect.y)
            self.big = True

    def damage(self, game):
        if self.invincible:
            return
        if self.big:
            bottom = self.rect.bottom
            self.rect.height = 38
            self.rect.bottom = bottom
            self.y = float(self.rect.y)
            self.big = False
            self.invincible = 100
            self.vy = -5
        else:
            game.lose_life()

    def update(self, keys, jump_held, solids, game):
        if self.invincible:
            self.invincible -= 1
        direction = int(keys[pygame.K_d] or keys[pygame.K_RIGHT]) - int(keys[pygame.K_a] or keys[pygame.K_LEFT])
        if direction:
            self.vx += direction * 0.68
            self.vx = max(-5.3, min(5.3, self.vx))
            self.facing = direction
        else:
            self.vx *= 0.77
            if abs(self.vx) < 0.1:
                self.vx = 0

        if jump_held and not self.jump_was_held and self.grounded:
            self.vy = -14.7
            self.grounded = False
        if not jump_held and self.jump_was_held and self.vy < -4.0:
            self.vy *= 0.42
        self.jump_was_held = jump_held

        # Strict axis separation: resolve all X penetration before Y motion.
        self.x += self.vx
        self.rect.x = round(self.x)
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vx > 0:
                    self.rect.right = solid.rect.left
                elif self.vx < 0:
                    self.rect.left = solid.rect.right
                self.x = float(self.rect.x)
                self.vx = 0

        self.vy = min(MAX_FALL, self.vy + GRAVITY)
        self.y += self.vy
        self.rect.y = round(self.y)
        self.grounded = False
        for solid in solids:
            if self.rect.colliderect(solid.rect):
                if self.vy > 0:
                    self.rect.bottom = solid.rect.top
                    self.grounded = True
                elif self.vy < 0:
                    self.rect.top = solid.rect.bottom
                    if isinstance(solid, QuestionBlock):
                        solid.hit(game)
                self.y = float(self.rect.y)
                self.vy = 0
        self.x = max(0.0, self.x)
        if self.rect.left < 0:
            self.rect.left = 0
            self.x = 0.0
            self.vx = 0
        if self.rect.top > HEIGHT + 100:
            game.lose_life()

    def draw(self, screen, camera, ticks):
        if self.invincible and (self.invincible // 5) % 2:
            return
        r = camera.screen(self.rect)
        red = (220, 53, 47)
        blue = (37, 92, 196)
        skin = (251, 187, 135)
        h = r.h
        pygame.draw.rect(screen, (70, 43, 33), (r.x + 3, r.bottom - 8, 11, 8))
        pygame.draw.rect(screen, (70, 43, 33), (r.right - 14, r.bottom - 8, 11, 8))
        pygame.draw.rect(screen, blue, (r.x + 6, r.y + int(h * 0.52), 18, int(h * 0.34)))
        pygame.draw.rect(screen, red, (r.x + 2, r.y + int(h * 0.36), 26, int(h * 0.23)))
        pygame.draw.rect(screen, skin, (r.x + 7, r.y + int(h * 0.17), 18, int(h * 0.28)))
        pygame.draw.rect(screen, red, (r.x + 3, r.y + 1, 24, 9))
        pygame.draw.rect(screen, red, (r.x + (5 if self.facing == 1 else 0), r.y + 8, 25, 5))
        eye_x = r.x + (21 if self.facing == 1 else 10)
        pygame.draw.circle(screen, (39, 39, 43), (eye_x, r.y + int(h * 0.27)), 2)
        pygame.draw.rect(screen, (247, 227, 179), (r.x + 2, r.y + int(h * 0.58), 5, 7))
        pygame.draw.rect(screen, (247, 227, 179), (r.right - 7, r.y + int(h * 0.58), 5, 7))
        if self.big:
            pygame.draw.rect(screen, (255, 215, 87), (r.x + 10, r.y + int(h * 0.57), 4, 4))
            pygame.draw.rect(screen, (255, 215, 87), (r.x + 18, r.y + int(h * 0.57), 4, 4))


class Flagpole:
    def __init__(self, x):
        self.rect = pygame.Rect(x, GROUND_Y - 260, 20, 260)

    def draw(self, screen, camera):
        r = camera.screen(self.rect)
        pygame.draw.rect(screen, (222, 229, 224), (r.x + 8, r.y, 6, r.h))
        pygame.draw.circle(screen, (255, 212, 68), (r.x + 11, r.y), 10)
        pygame.draw.polygon(screen, (239, 69, 70), [(r.x + 9, r.y + 17), (r.x - 70, r.y + 25), (r.x + 9, r.y + 67)])
        pygame.draw.rect(screen, (89, 96, 100), (r.x - 6, r.bottom - 12, 33, 12))


class Game:
    START_SCREEN, PLAYING, GAME_OVER, VICTORY = range(4)

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Ram's Mario - Python Platformer")
        self.clock = pygame.time.Clock()
        self.camera = Camera()
        self.state = self.START_SCREEN
        self.reset()
        self.state = self.START_SCREEN

    def reset(self):
        self.score = 0
        self.coins_collected = 0
        self.lives = 3
        self.camera.x = 0
        self.create_level()
        self.state = self.PLAYING

    def create_level(self):
        self.platforms = []
        self.blocks = []
        self.coins = []
        self.enemies = []
        self.powerups = []
        for start, end in ((0, 1056), (1200, 2208), (2352, 3408), (3552, WORLD_WIDTH)):
            for x in range(start, end, TILE):
                for y in range(GROUND_Y, HEIGHT, TILE):
                    self.platforms.append(Platform(x, y))
        for x, height in ((672, 72), (1536, 96), (2736, 96), (3168, 72)):
            self.platforms.append(Platform(x, GROUND_Y - height, 70, height, "pipe"))
        # Elevated groups: bricks, question blocks, and coin rewards.
        for x in (288, 336, 432, 480, 864, 912, 960, 1392, 1440,
                  1800, 1848, 1896, 2496, 2544, 2592, 2976, 3024):
            self.platforms.append(Platform(x, 370, kind="brick"))
        for x, reward in ((384, "coin"), (1008, "mushroom"), (1488, "coin"),
                          (1944, "mushroom"), (2640, "coin"), (3072, "mushroom")):
            self.blocks.append(QuestionBlock(x, 370, reward))
        # Final staircase halfway between the original and closer positions.
        for i in range(1, 5):
            for j in range(i):
                self.platforms.append(Platform(4008 + (i - 1) * TILE, GROUND_Y - (j + 1) * TILE,
                                               kind="brick"))
        for x, y in ((210, 440), (330, 326), (470, 326), (760, 395),
                     (910, 325), (1270, 445), (1450, 325), (1710, 430),
                     (1880, 325), (2100, 443), (2440, 445), (2570, 323),
                     (2900, 435), (3020, 325), (3310, 430), (3630, 435),
                     (3920, 280), (4150, 425), (4360, 440)):
            self.coins.append(Coin(x, y))
        for x in (535, 810, 1300, 1670, 2050, 2445, 2880, 3260, 3640, 4170):
            self.enemies.append(Enemy(x, GROUND_Y))
        self.flagpole = Flagpole(4480)
        self.player = Player(80, GROUND_Y - 38)

    def solids(self):
        return self.platforms + self.blocks

    def safe_respawn_x(self, death_x):
        """Find supported ground just behind the player, away from pipes/walls.

        The nearest safely supported position is chosen without rebuilding the
        level, so defeated enemies and collected coins stay collected.
        """
        solids = self.solids()
        for x in range(max(80, int(death_x) - 75), 79, -12):
            candidate = pygame.Rect(x, GROUND_Y - 38, 30, 38)
            # Require a continuous 50-pixel buffer on each side of the player.
            support = pygame.Rect(x - 50, GROUND_Y, 130, 4)
            supported = any(
                p.kind == "ground" and
                p.rect.top == GROUND_Y and
                p.rect.left <= support.left and
                p.rect.right >= support.right
                for p in self.platforms
            )
            # Ground is tiled, so check the union of the tiles, not one tile.
            if not supported:
                supported = all(
                    any(p.kind == "ground" and p.rect.collidepoint(px, GROUND_Y + 1)
                        for p in self.platforms)
                    for px in range(support.left, support.right, 10)
                )
            if supported and not any(candidate.colliderect(p.rect) for p in solids):
                return x
        return 80

    def lose_life(self):
        if self.state != self.PLAYING:
            return
        death_x = self.player.rect.x
        self.lives -= 1
        if self.lives <= 0:
            self.state = self.GAME_OVER
            return
        # Respawn close to where the player died, on safe ground.
        # Keep the current level and score rather than resetting progress.
        spawn_x = self.safe_respawn_x(death_x)
        self.player = Player(spawn_x, GROUND_Y - 38)
        self.player.invincible = 120
        self.camera.update(self.player)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if self.state == self.START_SCREEN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.state = self.PLAYING
                elif self.state in (self.GAME_OVER, self.VICTORY) and event.key in (pygame.K_r, pygame.K_RETURN):
                    self.reset()

    def update(self):
        if self.state != self.PLAYING:
            return
        keys = pygame.key.get_pressed()
        jump = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]
        solids = self.solids()
        active_player = self.player
        self.player.update(keys, jump, solids, self)
        # A death may replace the player and level during the update.
        # Stop this frame so stale collisions cannot affect the new life.
        if self.player is not active_player:
            return
        if self.state != self.PLAYING:
            return
        for block in self.blocks:
            block.update()
        for coin in self.coins[:]:
            coin.update()
            if self.player.rect.colliderect(coin.rect):
                self.coins.remove(coin)
                self.score += 100
                self.coins_collected += 1
        for powerup in self.powerups[:]:
            powerup.update(solids)
            if not powerup.alive:
                self.powerups.remove(powerup)
            elif self.player.rect.colliderect(powerup.rect):
                self.player.grow(solids)
                self.score += 500
                self.powerups.remove(powerup)
        for enemy in self.enemies[:]:
            enemy.update(solids, self.enemies)
            if not enemy.alive:
                if enemy.squash <= 0:
                    self.enemies.remove(enemy)
                continue
            if self.player.rect.colliderect(enemy.rect):
                old_bottom = self.player.rect.bottom - max(0, self.player.vy)
                stomp = self.player.vy > 0 and old_bottom <= enemy.rect.top + 12
                if stomp:
                    enemy.alive = False
                    enemy.squash = 18
                    self.player.rect.bottom = enemy.rect.top
                    self.player.y = float(self.player.rect.y)
                    self.player.vy = -9.5
                    self.score += 200
                else:
                    self.player.damage(self)
                    if self.state != self.PLAYING:
                        return
                    # A lost life rebuilds the enemy list; stop traversing stale objects.
                    if self.player.invincible == 90:
                        return
        if self.player.rect.colliderect(self.flagpole.rect):
            self.score += 1000
            self.state = self.VICTORY
        self.camera.update(self.player)

    def background(self):
        self.screen.fill(SKY)
        pygame.draw.rect(self.screen, (170, 227, 255), (0, 400, WIDTH, 200))
        # Distant hills use a slower camera displacement for parallax.
        for world_x in range(-200, WORLD_WIDTH + 600, 430):
            x = int(world_x - self.camera.x * 0.25)
            if -350 < x < WIDTH + 350:
                pygame.draw.ellipse(self.screen, (85, 185, 119), (x, 340, 330, 270))
                pygame.draw.ellipse(self.screen, (108, 209, 130), (x + 40, 365, 220, 240))
        for world_x in range(60, WORLD_WIDTH + 400, 390):
            x = int(world_x - self.camera.x * 0.45)
            y = 92 + (world_x // 390 % 3) * 43
            if -100 < x < WIDTH + 100:
                for dx, dy, rad in ((0, 18, 22), (27, 8, 29), (58, 19, 22)):
                    pygame.draw.circle(self.screen, (246, 251, 255), (x + dx, y + dy), rad)
                pygame.draw.rect(self.screen, (246, 251, 255), (x, y + 18, 58, 22))

    def draw_world(self):
        self.background()
        for platform in self.platforms:
            platform.draw(self.screen, self.camera)
        for block in self.blocks:
            block.draw(self.screen, self.camera)
        for coin in self.coins:
            coin.draw(self.screen, self.camera)
        for powerup in self.powerups:
            powerup.draw(self.screen, self.camera)
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)
        self.flagpole.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera, pygame.time.get_ticks())
        pygame.draw.rect(self.screen, (27, 48, 74), (0, 0, WIDTH, 51))
        draw_text(self.screen, f"SCORE {self.score:06d}", 22, (255, 255, 255), (145, 25), False)
        draw_text(self.screen, f"COINS {self.coins_collected:02d}", 22, (255, 221, 88), (405, 25), False)
        draw_text(self.screen, f"LIVES {self.lives}", 22, (255, 255, 255), (655, 25), False)

    def overlay(self, heading, subheading, hint):
        shade = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        shade.fill((18, 30, 57, 185))
        self.screen.blit(shade, (0, 0))
        draw_text(self.screen, heading, 49, (255, 219, 88), (400, 214))
        draw_text(self.screen, subheading, 23, (255, 255, 255), (400, 289))
        draw_text(self.screen, hint, 20, (201, 240, 255), (400, 348))

    def draw(self):
        self.draw_world()
        if self.state == self.START_SCREEN:
            self.overlay("RAM'S MARIO", "ONE LEVEL  |  THREE LIVES", "ENTER to start  |  WASD / Arrows  |  SPACE to jump")
        elif self.state == self.GAME_OVER:
            self.overlay("GAME OVER - NO LIVES LEFT", f"Final score: {self.score}", "Press R or ENTER to start over with 3 lives")
        elif self.state == self.VICTORY:
            self.overlay("YOU WIN!", f"Score: {self.score}   Coins: {self.coins_collected}", "Press R or ENTER to play again")
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()


if __name__ == "__main__":
    Game().run()
