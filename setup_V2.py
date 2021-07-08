import pygame
from pygame.surfarray import array3d
import os
import random
from pygame import *
import numpy as np
import cv2

# start up pygame
pygame.init()
clock = pygame.time.Clock()

# set up screen size, FPS, colors...
WINDOW_SIZE = (width, height) = (852, 302)
screen = pygame.display.set_mode(WINDOW_SIZE)

font = pygame.font.Font('freesansbold.ttf', 15)

GROUND_LEVEL = round(height * 0.83)  # equals 501,32
X_POSITION = round(width / 15)  # equals 56,8

# Define colours
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

FPS = 40

# set gravity
GRAVITY = 0.5

# set highscore
HIGHSCORE = 0


# create graphical objects (non-animated and animated respectively)
def load_image(name, sizex=-1, sizey=-1, colorkey=None):
    fullname = os.path.join('img', name)
    image = pygame.image.load(fullname)
    image = image.convert()

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)

    if sizex != -1 or sizey != -1:
        image = pygame.transform.scale(image, (sizex, sizey))

    return image, image.get_rect()


def load_sprite_sheet(sheetname, nx, ny, scalex=-1, scaley=-1, colorkey=None,):
    fullname = os.path.join('img', sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizey = sheet_rect.height / ny
    if isinstance(nx,int):
        sizex = sheet_rect.width / nx
        for i in range(0, ny):
            for j in range(0, nx):
                rect = pygame.Rect((j * sizex, i * sizey, sizex, sizey))
                image = pygame.Surface(rect.size)
                image = image.convert()
                image.blit(sheet, (0, 0), rect)

                if colorkey is not None:
                    if colorkey == -1:
                        colorkey = image.get_at((0, 0))
                    image.set_colorkey(colorkey, RLEACCEL)

                if scalex != -1 or scaley != -1:
                    image = pygame.transform.scale(image, (scalex, scaley))

                sprites.append(image)

    else:  # list
        sizex_ls = [sheet_rect.width / i_nx for i_nx in nx]
        for i in range(0, ny):
            for i_nx, sizex, i_scalex in zip(nx, sizex_ls, scalex):
                for j in range(0, i_nx):
                    rect = Rect((j * sizex, i * sizey, sizex, sizey))
                    image = Surface(rect.size)
                    image = image.convert()
                    image.blit(sheet, (0, 0), rect)

                    if colorkey is not None:
                        if colorkey is -1:
                            colorkey = image.get_at((0, 0))
                        image.set_colorkey(colorkey, RLEACCEL)

                    if i_scalex != -1 or scaley != -1:
                        image = transform.scale(image, (i_scalex, scaley))

                    sprites.append(image)

    sprite_rect = sprites[0].get_rect()

    return sprites, sprite_rect


def pre_processing(image, w, h):
    image = cv2.cvtColor(cv2.resize(image, (w, h)), cv2.COLOR_BGR2GRAY)
   # cv2.imwrite("color.jpg", image)
   # _, image = cv2.threshold(image, 1, 255, cv2.THRESH_BINARY)
    #cv2.imwrite("bw.jpg", image)
    # output 2D array
    return image[None, :, :].astype(np.float32)


# show background
class Background:
    def __init__(self, bg_speed):
        self.image, self.rect = load_image('background-black.png', -1, -1, 1)
        self.image1, self.rect1 = load_image('background-black.png', -1, -1, 1)
        self.rect.bottom = height
        self.rect1.bottom = height
        self.rect1.left = self.rect.right
        self.speed = bg_speed

    def draw(self):
        screen.blit(self.image, self.rect)
        screen.blit(self.image1, self.rect1)

    def update(self):
        self.rect.left += self.speed
        self.rect1.left += self.speed

        if self.rect.right < 0:
            self.rect.left = self.rect1.right

        if self.rect1.right < 0:
            self.rect1.left = self.rect.right


def show_score(score, HIGHSCORE):
    highscore_value = font.render("Highscore : " + str(HIGHSCORE), True, WHITE)
    screen.blit(highscore_value, (10, 10))
    score_value = font.render("Score : " + str(score), True, WHITE)
    screen.blit(score_value, (10, 30))


def draw_window(scrollingBg, enemies, score, HIGHSCORE):
#def draw_window(scrollingBg, enemies, fishes, score, HIGHSCORE):

    # define elements on screen
    scrollingBg.draw()
    show_score(score, HIGHSCORE)

    for enemy in enemies:
        enemy.draw(screen)
        enemy.move()

   # for fish in fishes:
    #    fish.draw(screen)
    #    fish.move()

    pygame.display.update()


# Player character
class Penguin:
    def __init__(self, sizex=-1, sizey=-1):
        self.images, self.rect = load_sprite_sheet('jump6.png', 6, 1, sizex, sizey, -1)
        self.images1, self.rect1 = load_sprite_sheet('slide_die.png', 3, 1, sizex, sizey, -1)
        # positions character
        self.rect.bottom = GROUND_LEVEL
        self.rect.left = X_POSITION
        self.image = self.images[0]
        self.image1 = self.images1[0]
        self.index = 0
        self.frame = 0
        self.isJumping = False
        self.isDucking = False
        self.isDead = False
        self.movement = [0, 0]
        self.jumpSpeed = 11
        self.x = self.rect.x
        self.y = self.rect.y

        self.stand_pos_width = self.rect.width
        self.duck_pos_width = self.rect1.width

    # draw self
    def draw(self):
        screen.blit(self.image, self.rect)

    # collision detection with the ground
    def checkbounds(self):
        if self.rect.bottom > GROUND_LEVEL:
            self.rect.bottom = GROUND_LEVEL
            self.isJumping = False

    # status checks (collect item, jump...)
    def update(self):
        if self.isJumping:
            self.movement[1] = self.movement[1] + GRAVITY
            self.index = 0
        # ducking
        elif self.isDucking:
            self.index = (self.index + 1) % 2
            self.index = 1
        # walking animation
        else:
            if self.frame % 5 == 0:
                self.index = (self.index + 1) % 5

        # hit animation
        if self.isDead:
            if not self.isDucking:
                self.index = 5
            if self.isDucking:
                self.index = 2

        # normal animation
        if not self.isDucking:
            self.image = self.images[self.index]
            self.rect.width = self.stand_pos_width
        else:
            self.image = self.images1[self.index]
            self.rect1.width = self.duck_pos_width

        self.rect = self.rect.move(self.movement)
        self.checkbounds()

        # score increases every 1/4 second
       # if not self.isDead and self.frame % 10 == 0:
        # advances frame counter every time character is updated (= 40 times per second as per FPS set and clock)
        self.frame = (self.frame + 1)

    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Enemy:
    def __init__(self, gamespeed):
        if random.choice(range(6)) > 2:
            self.type_ = 1  # snowman
            self.images, self.rect = load_sprite_sheet('snowman4.png', 4, 1, 64, 64, -1)
            self.image = self.images[0]
            self.rect.bottom = GROUND_LEVEL
            self.rect.left = width + self.rect.width
        else:
            self.type_ = 2  # bird
            self.images, self.rect = load_sprite_sheet('vogel3.png', 4, 1, 75, 90, -1)
            self.image = self.images[0]
            # self.bird_height = [height * 0.80, height * 0.90]
            self.bird_height = [height * 0.78, height * 0.78, height * 0.78, height * 0.90]
            self.rect.bottom = self.bird_height[random.randrange(0, 4)]
            self.rect.left = width + self.rect.width
        self.index = 0
        self.frame = 0
        self.movement = [-1 * gamespeed, 0]
        self.x = self.rect.x
        self.y = self.rect.y

    def move(self):
        self.rect = self.rect.move(self.movement)

    def collide(self, penguin):
        # Checking for collision using get mask function
        player_mask = penguin.get_mask()
        obj_mask = pygame.mask.from_surface(self.image)
        obj_offset = (round(self.rect.x - penguin.rect.x), self.rect.y - round(penguin.rect.y))
        collision_point = player_mask.overlap(obj_mask, obj_offset)
        if collision_point:
            return True
        return False

    def draw(self, screen):
        self.image = self.images[self.index]
        if self.type_ == 1:
            if self.frame % 10 == 0:
                self.index = (self.index + 1) % 3

        if self.type_ == 2:
            if self.frame % 6 == 0:
                # high birds have 1 frame of animation less for the old version
                if self.rect.bottom == (height * 0.90):
                    self.index = (self.index + 1) % 4
                if self.rect.bottom != (height * 0.90):
                    self.index = (self.index + 1) % 3

        self.frame = (self.frame + 1)
        screen.blit(self.image, self.rect)
        # pygame.draw.rect(screen, RED, self.rect, 2)


# Bonus item
class Fish:
    def __init__(self, x, y):
        self.image, self.rect = load_image('fisch3.png', x, y, -1)
        self.fish_height = [height * 0.59, height * 0.75, height * 0.82]
        self.rect.bottom = self.fish_height[random.randrange(0, 3)]
        self.rect.left = width + self.rect.width
        self.speed = 18
        self.movement = [-1 * self.speed, 0]
        self.passed = False

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def move(self):
        self.rect = self.rect.move(self.movement)

    def collide(self, penguin):
        # Checking for collision using get mask function
        player_mask = penguin.get_mask()
        obj_mask = pygame.mask.from_surface(self.image)
        obj_offset = (round(self.rect.x - penguin.rect.x), self.rect.y - round(penguin.rect.y))
        collision_point = player_mask.overlap(obj_mask, obj_offset)
        if collision_point:
            return True
        return False


class DQNAgent(object):
    def __init__(self):
        display.set_caption("DeepRunnerDQN")
        self.screen_width = 852
        self.screen_height = 604
        self.gamespeed = 4
        self.bg_speed = 4
        self.gameOver = False
        self.gameQuit = False
        self.penguin = Penguin(72, 64)
        self.scrollingBg = Background(-1 * self.bg_speed)
        self.frame = 0
        self.score = 0
        self.enemies = [Enemy(self.gamespeed)]
       # self.fishes = [Fish(45, 25)]
        self.last_obstacle = None

    def step(self, action, record=False):  # 0: Do nothing. 1: Jump. 2: Duck
        global HIGHSCORE
        reward = 0.1
        if action == 0:
            reward += 0.01
            self.penguin.isDucking = False
        elif action == 1:
            self.penguin.isDucking = False
            if self.penguin.rect.bottom == GROUND_LEVEL:
                self.penguin.isJumping = True
                self.penguin.movement[1] = -1 * self.penguin.jumpSpeed
        elif action == 2:
            if not (self.penguin.isJumping and self.penguin.isDead) and self.penguin.rect.bottom == GROUND_LEVEL:
                self.penguin.isDucking = True

        for enemy in self.enemies:
            enemy.movement[0] = -1 * self.gamespeed
            enemy.move()
            if enemy.collide(self.penguin):
                self.penguin.isDead = True
                reward = -1
                break
            else:
                if enemy.rect.right < self.penguin.rect.left:
                    reward = 1
                    if enemy.rect.x <= 0:
                        self.enemies.clear()
                        self.enemies.append(Enemy(self.gamespeed))
                        enemy.move()
                        break

       # for fish in self.fishes:
        #    if fish.collide(self.penguin):
             #   reward = 0.5
             #   self.score += 50
         #       self.fishes.clear()
         #       self.fishes.append(Fish(45, 25))
         #   elif fish.rect.right <= 0:
          #      self.fishes.clear()
           #     self.fishes.append(Fish(45, 25))
           #     break

        self.penguin.update()
        self.scrollingBg.update()

        # score increases every 1/4 second
        if self.frame % 10 == 0:
            self.score += 1

        # Update screen
        draw_window(self.scrollingBg, self.enemies, self.score, HIGHSCORE)
#        draw_window(self.scrollingBg, self.fishes, self.enemies, self.score, HIGHSCORE)

        self.frame += 1

        #pygame.display.update()

        self.penguin.draw()
        self.penguin.update()

        if self.penguin.isDead:
            self.gameOver = True
            if self.score > HIGHSCORE:
                HIGHSCORE = self.score

        if self.gameOver:
            self.__init__()

        state = array3d(display.get_surface())
        display.update()
        clock.tick(FPS)
        # penguin dies

        return state, reward, not (reward > 0)
