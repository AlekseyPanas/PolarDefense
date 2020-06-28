import pygame
import math
from PIL import Image, ImageFilter
pygame.init()

SCREEN_SIZE = (900, 900)
valid = False
while not valid:
    SCREEN_SIZE = input("Please enter a single value screen size in pixels: ")
    try:
        SCREEN_SIZE = int(SCREEN_SIZE)
        valid = True
    except Exception:
        print("Please enter a valid screen size")
        valid = False
SCREEN_SIZE = tuple([SCREEN_SIZE for x in range(2)])

# Water friction for enemies
FRICTION = 0.994


def convert():
    global TURRET_IMAGE, OCEAN_IMAGE, ISLAND_IMAGE, FIELD_IMAGE, CALIBRATE_IMAGE, EXPLOSION_IMAGE, JET_CHARGER_IMAGE, \
        TUT_1_IMG, TUT_2_IMG, TUT_3_IMG, TUT_4_IMG, TUT_5_IMG, TUT_6_IMG, TUT_7_IMG, NEXT_BUTTON, SKIP_BUTTON, \
        YES_BUTTON, NO_BUTTON, BACK_BUTTON, LOGO_IMAGE, TUTORIAL_BUTTON, QUIT_BUTTON, LEVELS_BUTTON, LOCK_IMAGE, \
        START_BAR_IMAGE, START_BUTTON, GAMEOVER_IMAGE, LEVEL_COMPLETE_IMAGE, MENU_BUTTON, BUOY_IMAGE

    TURRET_IMAGE = TURRET_IMAGE.convert_alpha()
    OCEAN_IMAGE = OCEAN_IMAGE.convert_alpha()
    ISLAND_IMAGE = ISLAND_IMAGE.convert_alpha()
    FIELD_IMAGE = FIELD_IMAGE.convert_alpha()
    CALIBRATE_IMAGE = CALIBRATE_IMAGE.convert_alpha()
    EXPLOSION_IMAGE = EXPLOSION_IMAGE.convert_alpha()
    JET_CHARGER_IMAGE = JET_CHARGER_IMAGE.convert_alpha()
    TUT_1_IMG = TUT_1_IMG.convert_alpha()
    TUT_2_IMG = TUT_2_IMG.convert_alpha()
    TUT_3_IMG = TUT_3_IMG.convert_alpha()
    TUT_4_IMG = TUT_4_IMG.convert_alpha()
    TUT_5_IMG = TUT_5_IMG.convert_alpha()
    TUT_6_IMG = TUT_6_IMG.convert_alpha()
    TUT_7_IMG = TUT_7_IMG.convert_alpha()
    SKIP_BUTTON = SKIP_BUTTON.convert_alpha()
    NEXT_BUTTON = NEXT_BUTTON.convert_alpha()
    BACK_BUTTON = BACK_BUTTON.convert_alpha()
    NO_BUTTON = NO_BUTTON.convert_alpha()
    YES_BUTTON = YES_BUTTON.convert_alpha()
    LOGO_IMAGE = LOGO_IMAGE.convert_alpha()
    TUTORIAL_BUTTON = TUTORIAL_BUTTON.convert_alpha()
    QUIT_BUTTON = QUIT_BUTTON.convert_alpha()
    LEVELS_BUTTON = LEVELS_BUTTON.convert_alpha()
    LOCK_IMAGE = LOCK_IMAGE.convert_alpha()
    START_BAR_IMAGE = START_BAR_IMAGE.convert_alpha()
    START_BUTTON = START_BUTTON.convert_alpha()
    GAMEOVER_IMAGE = GAMEOVER_IMAGE.convert_alpha()
    LEVEL_COMPLETE_IMAGE = LEVEL_COMPLETE_IMAGE.convert_alpha()
    MENU_BUTTON = MENU_BUTTON.convert_alpha()
    BUOY_IMAGE = BUOY_IMAGE.convert_alpha()


# Creates a glow light to be drawn under the units when selected
def create_shadow(size, color):
    surface = pygame.Surface((size[0] + 50, size[1] + 50), pygame.SRCALPHA, 32)
    surface = surface.convert_alpha()

    pygame.draw.rect(surface, color, (25, 25, size[0], size[1]))

    # Blurs the rect surface
    surface = Image.frombytes('RGBA', surface.get_size(),
                                  pygame.image.tostring(surface, 'RGBA', False)).filter(
        ImageFilter.GaussianBlur(radius=7))
    surface = pygame.image.frombuffer(surface.tobytes(), surface.size,
                                                  surface.mode)

    # This is how you set the transparency of this surface if needed
    surface.fill((255, 255, 255, 200), None, pygame.BLEND_RGBA_MULT)

    return surface


def blur_surface(surf, radius):
    # Blurs the rect surface
    surface = Image.frombytes('RGBA', surf.get_size(),
                              pygame.image.tostring(surf, 'RGBA', False)).filter(
        ImageFilter.GaussianBlur(radius=radius))
    surface = pygame.image.frombuffer(surface.tobytes(), surface.size,
                                      surface.mode)
    return surface


# Scales a set of coordinates to the current screen size based on a divisor factor
def cscale(*coordinate, divisor=900):
    if len(coordinate) > 1:
        return tuple([int(coordinate[x] / divisor * SCREEN_SIZE[x % 2]) for x in range(len(coordinate))])
    else:
        return int(coordinate[0] / divisor * SCREEN_SIZE[0])


# Scales a set of coordinates to the current screen size based on a divisor factor. Doesn't return integers
def posscale(*coordinate, divisor=900):
    if len(coordinate) > 1:
        return tuple([coordinate[x] / divisor * SCREEN_SIZE[x] for x in range(len(coordinate))])
    else:
        return coordinate[0] / divisor * SCREEN_SIZE[0]


def get_pos_from_angle_and_radius(origin, angle, radius):
    # Rescales the radius based on the screen size
    new_radius = (radius / 900) * SCREEN_SIZE[0]

    return (origin[0] + new_radius * math.cos(math.radians(angle)),
            origin[1] - new_radius * math.sin(math.radians(angle)))


def distance(a, b):
    return math.sqrt((b[1] - a[1]) ** 2 + (b[0] - a[0]) ** 2)


# Image loading
TURRET_IMAGE = pygame.transform.scale(pygame.image.load('assets/Turret.png'), (int((372/2700) * SCREEN_SIZE[0]), int((219/2700) * SCREEN_SIZE[1])))
OCEAN_IMAGE = pygame.transform.scale(pygame.image.load('assets/Ocean.png'), SCREEN_SIZE)
ISLAND_IMAGE = pygame.transform.scale(pygame.image.load('assets/island.png'), (int((92/500) * SCREEN_SIZE[0]), int((66/500) * SCREEN_SIZE[1])))
FIELD_IMAGE = pygame.image.load("assets/field.png")
CALIBRATE_IMAGE = pygame.image.load("assets/CalibrateButton.png")
EXPLOSION_IMAGE = pygame.transform.scale(pygame.image.load("assets/explosion.png"), (int(SCREEN_SIZE[0] / .9), int(SCREEN_SIZE[1] / .9)))
LOCK_IMAGE = pygame.transform.scale(pygame.image.load("assets/lock_icon.png"), cscale(50, 50))
START_BAR_IMAGE = pygame.transform.scale(pygame.image.load("assets/Start_Bar.png"), cscale(900, 40))
GAMEOVER_IMAGE = pygame.transform.scale(pygame.image.load("assets/gameover.png"), cscale(300, 45))
LEVEL_COMPLETE_IMAGE = pygame.transform.scale(pygame.image.load("assets/lvl_comp.png"), cscale(300, 45))
BUOY_IMAGE = pygame.transform.scale(pygame.image.load("assets/Buoy.png"), cscale(40, 78))

NEXT_BUTTON = pygame.image.load("assets/NextButton.png")
SKIP_BUTTON = pygame.image.load("assets/SkipButton.png")
BACK_BUTTON = pygame.image.load("assets/Back_Button.png")
LEVELS_BUTTON = pygame.image.load("assets/Levels_Button.png")
TUTORIAL_BUTTON = pygame.image.load("assets/Tutorial_Button.png")
QUIT_BUTTON = pygame.image.load("assets/Quit_Button.png")
NO_BUTTON = pygame.image.load("assets/No_Button.png")
YES_BUTTON = pygame.image.load("assets/Yes_Button.png")
START_BUTTON = pygame.image.load("assets/Start_Button.png")
MENU_BUTTON = pygame.image.load("assets/Menu_Button.png")

LOGO_IMAGE = pygame.transform.scale(pygame.image.load("assets/Logo.png"), cscale(845, 184))
# Enemy Ships
JET_CHARGER_IMAGE = pygame.transform.scale(pygame.image.load("assets/JetShip_NoGun.png"), (int((300 / 2800) * SCREEN_SIZE[0]), int((145 / 2800) * SCREEN_SIZE[0])))
# Tutorial pages
TUT_1_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_1.png"), SCREEN_SIZE)
TUT_2_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_2.png"), SCREEN_SIZE)
TUT_3_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_3.png"), SCREEN_SIZE)
TUT_4_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_4.png"), SCREEN_SIZE)
TUT_5_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_5.png"), SCREEN_SIZE)
TUT_6_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_6.png"), SCREEN_SIZE)
TUT_7_IMG = pygame.transform.scale(pygame.image.load("assets/Tutorial_7.png"), SCREEN_SIZE)

# Fonts
HELVETICA_FONT = pygame.font.SysFont("Helvetica", int(0.03 * SCREEN_SIZE[1]))
TIMES_FONT = pygame.font.SysFont("Times New Roman", int(0.02 * SCREEN_SIZE[1]))
COURIER_FONT = pygame.font.SysFont("Courier New Regular", int(0.02 * SCREEN_SIZE[1]))
BIGBOI_FONT = pygame.font.SysFont("Comic Sans", int(0.05 * SCREEN_SIZE[1]))
VERY_BIGBOI_FONT = pygame.font.SysFont("Comic Sans", int(0.1 * SCREEN_SIZE[1]))
