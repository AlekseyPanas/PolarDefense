import pygame
import math
pygame.init()

SCREEN_SIZE = (900, 900)


def convert():
    global TURRET_IMAGE, OCEAN_IMAGE, ISLAND_IMAGE, FIELD_IMAGE, CALIBRATE_IMAGE, EXPLOSION_IMAGE
    TURRET_IMAGE = TURRET_IMAGE.convert_alpha()
    OCEAN_IMAGE = OCEAN_IMAGE.convert_alpha()
    ISLAND_IMAGE = ISLAND_IMAGE.convert_alpha()
    FIELD_IMAGE = FIELD_IMAGE.convert_alpha()
    CALIBRATE_IMAGE = CALIBRATE_IMAGE.convert_alpha()
    EXPLOSION_IMAGE = EXPLOSION_IMAGE.convert_alpha()


def get_pos_from_angle_and_radius(origin, angle, radius):
    return (origin[0] + radius * math.cos(math.radians(angle)),
            origin[1] - radius * math.sin(math.radians(angle)))


# Image loading
TURRET_IMAGE = pygame.transform.scale(pygame.image.load('assets/Turret.png'), (int((372/2700) * SCREEN_SIZE[0]), int((219/2700) * SCREEN_SIZE[1])))
OCEAN_IMAGE = pygame.transform.scale(pygame.transform.scale(pygame.image.load('assets/Ocean.png'), SCREEN_SIZE), SCREEN_SIZE)
ISLAND_IMAGE = pygame.transform.scale(pygame.image.load('assets/island.png'), (int((92/500) * SCREEN_SIZE[0]), int((66/500) * SCREEN_SIZE[1])))
FIELD_IMAGE = pygame.image.load("assets/field.png")
CALIBRATE_IMAGE = pygame.image.load("assets/CalibrateButton.png")
EXPLOSION_IMAGE = pygame.transform.scale(pygame.image.load("assets/explosion.png"), (int(SCREEN_SIZE[0] / .9), int(SCREEN_SIZE[1] / .9)))

# Fonts
HELVETICA_FONT = pygame.font.SysFont("Helvetica", int(0.03 * SCREEN_SIZE[1]))
TIMES_FONT = pygame.font.SysFont("Times New Roman", int(0.02 * SCREEN_SIZE[1]))
