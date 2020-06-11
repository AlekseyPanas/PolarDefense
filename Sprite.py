import Constants
import pygame
import math
import TypeField
import Globe
import Button
import copy
import random


class Object:
    def __init__(self, lifetime, z_order):
        self.lifetime = lifetime
        self.kill = False

        self.z_order = z_order

    @staticmethod
    def rotate(image, rect, angle):
        """Rotate the image while keeping its center."""
        # Rotate the original image without modifying it.
        new_image = pygame.transform.rotate(image, angle)
        # Get a new rect with the center of the old rect.
        rect = new_image.get_rect(center=rect.center)
        return new_image, rect

    def run_sprite(self, screen):
        pass


class Animation(Object):
    def __init__(self, lifetime, z_order, sheet_dimensions, animation_speed, sheet, center, frame_count):
        # If none is entered for lifetime, the lifetime is set to -1 iteration of the animation
        if lifetime == -1:
            life = frame_count * animation_speed - 1
        else:
            life = lifetime
        super().__init__(life, z_order)

        # The dimensions of the sprite sheet by frame count (width, height)
        self.sheet_dimensions = sheet_dimensions
        # The amount of game ticks that should pass between each frame
        self.animation_speed = animation_speed

        self.sheet_frames_w = sheet_dimensions[0]
        self.sheet_frames_h = sheet_dimensions[1]

        # The sprite sheet image
        self.sheet = sheet
        # Dimensions of an individual frame
        self.frame_width = self.sheet.get_width() / self.sheet_frames_w
        self.frame_height = self.sheet.get_height() / self.sheet_frames_h

        # Center position of the animation
        self.pos = center

        # Counts the ticks. Used for reference in the animation calculations
        self.tick = 0
        # Gives the current frame number
        self.frame = 1
        # Gets the vertical and horizontal frame coordinates to point to the current frame
        self.frame_pos = [0, 0]
        # Total # of frames in sheet
        self.frame_count = frame_count

        # Surface onto which the animation will be drawn
        self.surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA, 32)

    def run_sprite(self, screen):
        # Draws animation
        if self.tick % self.animation_speed == 0:
            # Calculates the sheet position of frame
            horizontal_pos = self.frame % self.sheet_frames_w
            self.frame_pos = ((horizontal_pos if not horizontal_pos == 0 else 9) - 1, int(self.frame / self.sheet_frames_h - .01))
            self.surface.fill((255, 255, 255, 0))

            # Resets frame when it finishes cycling the sheet
            self.frame += 1
            if self.frame > self.frame_count:
                self.frame = 1
            # Shifts the sheet accordingly and blits the frame onto the surface
            self.surface.blit(self.sheet, (-self.frame_pos[0] * self.frame_width, -self.frame_pos[1] * self.frame_height))
        # Blits surface onto screen
        screen.blit(self.surface, (self.pos[0] - self.frame_width / 2, self.pos[1] - self.frame_height / 2))

        self.tick += 1


class TurretLaser(Object):
    def __init__(self, lifetime, z_order, origin, angle, radius):
        super().__init__(lifetime if lifetime is not None else 30, z_order)

        # Saves the total lifetime so it can be referenced later
        self.lifetime_save = copy.copy(self.lifetime)

        # Starting point of the laser
        self.origin = origin
        # Angle of gun from which laser is fired
        self.angle = angle
        # Length of laser shot
        self.radius = radius

        # Lazy mode. Takes a surface the size of the entire screen
        self.surface = pygame.Surface(Constants.SCREEN_SIZE, pygame.SRCALPHA)

    def run_sprite(self, screen):
        # Uses the given angle, radius, and origin to draw a red laser line
        # The laser line has an opacity which is proportionally based on the lifetime
        pygame.draw.line(self.surface, (255, 0, 0, (self.lifetime * 255) / self.lifetime_save), self.origin, Constants.get_pos_from_angle_and_radius(self.origin, self.angle, self.radius), 6)

        screen.blit(self.surface, (0, 0))


class Turret(Object):
    def __init__(self, lifetime, z_order, turret_center, typefield_top_left, calibrate_tick_duration, recoil):
        super().__init__(lifetime, z_order)

        # The center of the turret
        self.center = turret_center

        self.image = Constants.TURRET_IMAGE
        self.image_rect = self.image.get_rect()
        self.image_rect.center = self.center

        # The angle to which the turret is heading
        self.desired_angle = 0

        # The actual current angle of the turret
        self.angle = 0
        # The actual radius of the shot for the turret
        self.radius = 0

        # The angular recoil after each shot
        self.recoil = recoil

        # The top left corner where the type fields will be drawn
        self.type_topleft = typefield_top_left

        # Type field objects for entering angle and radius
        self.angle_field = TypeField.Field(self.type_topleft, Constants.SCREEN_SIZE[0] / 6, Constants.HELVETICA_FONT, Constants.FIELD_IMAGE, False)
        self.radius_field = TypeField.Field((self.type_topleft[0] + Constants.SCREEN_SIZE[0] / 5.8, self.type_topleft[1]), Constants.SCREEN_SIZE[0] / 6, Constants.HELVETICA_FONT, Constants.FIELD_IMAGE, True)

        # Renders Type field text labels
        self.angle_field_label = Constants.TIMES_FONT.render("Angle:", False, (255, 255, 255))
        self.radius_field_label = Constants.TIMES_FONT.render("Radius:", False, (255, 255, 255))

        # Calibrate button for the game
        self.calibrate_button = Button.Button((int(self.type_topleft[0] + 2.2 * (Constants.SCREEN_SIZE[0] / 5.8)), int(Constants.SCREEN_SIZE[1] / 200)),
                                              (int(Constants.SCREEN_SIZE[0] / 8), int(Constants.SCREEN_SIZE[0] / 18)), Constants.CALIBRATE_IMAGE)

        # The cool down between calibrations
        self.calib_duration = calibrate_tick_duration
        # Calibration cooldown counter
        self.calib_count = 0

    def press_calibrate(self):
        self.calibrate_button.button_state = "pressed"
        self.calib_count += self.calib_duration
        # Sets the desired angle
        if self.angle_field.text == "" or self.angle_field.text == "-":
            ang = 0
        else:
            ang = self.angle_field.text
        self.desired_angle = float(ang)
        # Sets the desired radius
        if self.radius_field.text == "" or self.radius_field.text == "-":
            rad = 0
        else:
            rad = self.radius_field.text
        self.radius = float(rad)

    def run_sprite(self, screen):
        self.update()
        self.draw_turret(screen)

        self.angle_field.draw_handler(screen)
        self.radius_field.draw_handler(screen)

        self.event_handler()

        screen.blit(self.angle_field_label, (self.angle_field.pos[0], 0))
        screen.blit(self.radius_field_label, (self.radius_field.pos[0], 0))

        self.calibrate_button.is_hover(pygame.mouse.get_pos())
        self.calibrate_button.draw(screen)

    def event_handler(self):
        for event in Globe.events:
            self.angle_field.event_handler(event)
            self.radius_field.event_handler(event)

            if event.type == pygame.MOUSEBUTTONUP:
                # Checks if calibrate button is pressed and starts the cool down
                if self.calibrate_button.is_clicked(event.pos) and self.calib_count == 0:
                    self.press_calibrate()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_RETURN and self.calib_count == 0:
                    self.press_calibrate()

                if event.key == pygame.K_SPACE:
                    Globe.GAME.add_sprite(TurretLaser(None, 0, self.image_rect.center, self.angle, self.radius))
                    Globe.GAME.add_sprite(Animation(-1, 5, (9, 9), 2, Constants.EXPLOSION_IMAGE, Constants.get_pos_from_angle_and_radius(self.image_rect.center, self.angle, self.radius), 74))

                    # Adds recoil
                    self.desired_angle += random.randint(-self.recoil, self.recoil)

    def update(self):
        # MOUSE FOLLOW TEST
        # mouse = pygame.mouse.get_pos()
        # cent = self.image_rect.center
        # self.desired_angle = -math.degrees(math.atan2((mouse[1] - cent[1]), (mouse[0] - cent[0])))

        # Makes the current angle continuously approach the desired angle
        self.angle += round((self.desired_angle - self.angle) / 13, 1)

        # Counts down the cool down
        if self.calib_count > 1:
            self.calib_count -= 1
        # Resets the button once cool down wears off
        elif self.calib_count == 1:
            self.calibrate_button.button_state = "static"
            self.calib_count = 0

    def draw_turret(self, screen):
        self.image, self.image_rect = Object.rotate(Constants.TURRET_IMAGE, self.image_rect, self.angle)

        screen.blit(self.image, self.image_rect)
