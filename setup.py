import random
import sys
from pygame.locals import *
import os
import numpy as np
import pygame

# start up pygame
pygame.init()
clock = pygame.time.Clock()

# set up screen size, FPS, colors...
WINDOW_SIZE = (width, height) = (852, 604)
screen = pygame.display.set_mode(WINDOW_SIZE)
pygame.display.set_caption("DeepRunnerDQN")

font = pygame.font.Font('freesansbold.ttf', 20)

GROUND_LEVEL = round(height * 0.83) # equals 501,32
X_POSITION = round(width / 15) # equals 56,8

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
highscore = 0


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


def load_sprite_sheet(sheetname, nx, ny, scalex=-1, scaley=-1, colorkey=None):
    fullname = os.path.join('img', sheetname)
    sheet = pygame.image.load(fullname)
    sheet = sheet.convert()

    sheet_rect = sheet.get_rect()

    sprites = []

    sizex = sheet_rect.width / nx
    sizey = sheet_rect.height / ny

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

    sprite_rect = sprites[0].get_rect()

    return sprites, sprite_rect


# show score
def show_score(score):
    font = pygame.font.Font('freesansbold.ttf', 18)
    score_value = font.render("Score : " + str(score), True, WHITE)
    screen.blit(score_value, 10, 10)


def show_highscore(highscore):
    font = pygame.font.Font('freesansbold.ttf', 18)
    highscore_value = font.render("Highscore : " + str(highscore), True, WHITE)
    screen.blit(highscore_value, 10, 20)


# show background
class Background:
    def __init__(self, bg_speed):
        self.image, self.rect = load_image('bg_happy.png', -1, -1, 1)
        self.image1, self.rect1 = load_image('bg_happy.png', -1, -1, 1)
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