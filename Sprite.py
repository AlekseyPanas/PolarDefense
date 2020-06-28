import Constants
import pygame
import math
import TypeField
import Globe
import Button
import copy
import random


class Object:
    def __init__(self, lifetime, z_order, tags):
        self.lifetime = lifetime
        self.kill = False

        # Draw order
        self.z_order = z_order

        # Set of string tags that can identify an object
        self.tags = set(tags)

    @staticmethod
    def rotate(image, rect, angle):
        """Rotate the image while keeping its center."""
        # Rotate the original image without modifying it.
        new_image = pygame.transform.rotate(image, angle)
        # Get a new rect with the center of the old rect.
        rect = new_image.get_rect(center=rect.center)
        return new_image, rect

    def run_sprite(self, screen, update_lock):
        pass


'''
INFLATE SURFACE CLASS
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
'''


# Takes a surface along with 2 scale factors (ie. .3, 1.5, 2, etc)
# Uses the scale factors combined with the time to make the object grow on screen over time
# Includes additional option allowing the user to fade the object
class InflateSurface(Object):
    def __init__(self, lifetime, z_order, tags, surface, start_scale, stop_scale, scale_time, pos, fade=False,
                 initial_opacity=255, delay_inflation=0):
        super().__init__(lifetime, z_order, tags)

        self.surface_rect = surface.get_rect()

        self.pos = pos

        self.start_scale = (self.surface_rect.w * start_scale, self.surface_rect.h * start_scale)
        self.stop_scale = (self.surface_rect.w * stop_scale, self.surface_rect.h * stop_scale)
        self.scale_time = scale_time
        self.current_scale = list(copy.copy(self.start_scale))
        self.scale_increment = ((self.stop_scale[0] - self.start_scale[0]) / self.scale_time,
                                (self.stop_scale[1] - self.start_scale[1]) / self.scale_time)

        self.surface = pygame.Surface(self.surface_rect.size, pygame.SRCALPHA, 32)
        self.surface.blit(surface, (0, 0))

        self.opacity = initial_opacity
        self.fade_increment = (self.opacity + 1) / self.scale_time
        self.fade = fade

        # Delays inflation for a given amount of time
        self.delay_inflation = delay_inflation

    def run_sprite(self, screen, update_lock):
        if not update_lock:
            if self.delay_inflation == 0:
                self.update()
            else:
                self.delay_inflation -= 1
        self.draw(screen)

    def update(self):
        if self.current_scale[0] < self.stop_scale[0]:
            self.current_scale[0] += self.scale_increment[0]
            self.current_scale[1] += self.scale_increment[1]
        if self.fade:
            self.opacity -= self.fade_increment

    def draw(self, screen):
        new_surf = pygame.transform.scale(self.surface, [int(x) for x in self.current_scale]).convert_alpha()
        rect = new_surf.get_rect()
        rect.center = self.pos

        if self.fade:
            new_surf.fill((255, 255, 255, self.opacity if self.opacity >= 0 else 0), None, pygame.BLEND_RGBA_MULT)

        screen.blit(new_surf, rect)


'''
ANIMATION CLASS
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
'''


class Animation(Object):
    def __init__(self, lifetime, z_order, tags, sheet_dimensions, animation_speed, sheet, center, frame_count, binder=None):
        # If none is entered for lifetime, the lifetime is set to -1 iteration of the animation
        if lifetime == -1:
            life = frame_count * animation_speed - 1
        else:
            life = lifetime
        super().__init__(life, z_order, tags)

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

        # Refers to another object to which this one is bound. The explosion will follow the binder object
        self.binder = binder

        # Surface onto which the animation will be drawn
        self.surface = pygame.Surface((self.frame_width, self.frame_height), pygame.SRCALPHA, 32)
        # Calls update once to blit the first frame and resets the tick
        self.surface.blit(self.sheet, (0, 0))

    def run_sprite(self, screen, update_lock):
        if not update_lock:
            self.update()
        self.draw_sprite(screen)

    def update(self):
        # If bound, change position
        if self.binder is not None:
            self.pos = self.binder.pos

        # Updates
        if self.tick % self.animation_speed == 0:
            # Calculates the sheet position of frame
            horizontal_pos = self.frame % self.sheet_frames_w
            self.frame_pos = ((horizontal_pos if not horizontal_pos == 0 else 9) - 1, int(self.frame / self.sheet_frames_h - .01))
            # Clears surface
            self.surface.fill((255, 255, 255, 0))

            # Resets frame when it finishes cycling the sheet
            self.frame += 1
            if self.frame > self.frame_count:
                self.frame = 1

            # Shifts the sheet accordingly and blits the frame onto the surface
            self.surface.blit(self.sheet,
                              (-self.frame_pos[0] * self.frame_width, -self.frame_pos[1] * self.frame_height))

        self.tick += 1

    def draw_sprite(self, screen):
        # Blits surface onto screen
        screen.blit(self.surface, (self.pos[0] - self.frame_width / 2, self.pos[1] - self.frame_height / 2))


'''
TURRET LASER CLASS
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
'''


class TurretLaser(Object):
    def __init__(self, lifetime, z_order, tags, origin, angle, radius, color=(255, 0, 0)):
        super().__init__(lifetime if lifetime is not None else 30, z_order, tags)

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

        self.tags.add("Laser")

        self.color = color

    def run_sprite(self, screen, update_lock):
        if not update_lock:
            self.update()
        self.draw(screen)

    def update(self):
        # Uses the given angle, radius, and origin to draw a red laser line
        # The laser line has an opacity which is proportionally based on the lifetime
        pygame.draw.line(self.surface, (self.color[0], self.color[1], self.color[2], (self.lifetime * 255) / self.lifetime_save), self.origin,
                         Constants.get_pos_from_angle_and_radius(self.origin, self.angle, self.radius),
                         int((6 / 900) * Constants.SCREEN_SIZE[0]))

    def draw(self, screen):
        screen.blit(self.surface, (0, 0))


'''
TURRET CLASS
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
'''


class Turret(Object):
    def __init__(self, lifetime, z_order, tags, turret_center, typefield_top_left, calibrate_tick_duration, recoil,
                 display_mode=False, explosion_sheet=Constants.EXPLOSION_IMAGE, explosion_sheet_frames=74,
                 explosion_sheet_dims=(9, 9), turret_image=Constants.TURRET_IMAGE):
        super().__init__(lifetime, z_order, tags)

        # The center of the turret
        self.center = turret_center

        self.image_save = turret_image
        self.image = copy.copy(turret_image)
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
        self.angle_field = TypeField.Field(self.type_topleft, Constants.SCREEN_SIZE[0] / 6, Constants.HELVETICA_FONT, Constants.FIELD_IMAGE, False, None)
        self.radius_field = TypeField.Field((self.type_topleft[0] + Constants.SCREEN_SIZE[0] / 5.8, self.type_topleft[1]), Constants.SCREEN_SIZE[0] / 6, Constants.HELVETICA_FONT, Constants.FIELD_IMAGE, True, 75)

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

        # When angle reaches close enough to the desired angle, this determines when the angles get set to each other
        self.fixated_angle = False

        # Draws the turret without the input fields and buttons
        self.display_mode = display_mode

        # Used for custom explosion sprite sheets
        self.explosion_sheet = explosion_sheet
        self.explosion_sheet_frames = explosion_sheet_frames
        self.explosion_sheet_dims = explosion_sheet_dims

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

    def run_sprite(self, screen, update_lock):
        if not update_lock:
            self.update()
        self.draw(screen)

    def draw(self, screen):
        self.draw_turret(screen)

        if not self.display_mode:
            self.angle_field.draw_handler(screen)
            self.radius_field.draw_handler(screen)

            screen.blit(self.angle_field_label, (self.angle_field.pos[0], 0))
            screen.blit(self.radius_field_label, (self.radius_field.pos[0], 0))

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
                if event.key == pygame.K_SPACE and int(self.angle) == int(self.desired_angle):
                    self.shoot()

    def shoot(self):
        # Ensures the radius stays within the minimum value
        self.radius = self.radius if self.radius >= self.radius_field.minimum_value else self.radius_field.minimum_value

        collide_point = Constants.get_pos_from_angle_and_radius(self.image_rect.center, self.angle, self.radius)

        if not self.display_mode:
            Globe.MENU.GAME.add_sprite(TurretLaser(None, 0, {}, self.image_rect.center, self.angle, self.radius))
            Globe.MENU.GAME.add_sprite(Animation(-1, 5, {}, self.explosion_sheet_dims, 2, self.explosion_sheet,
                                                     collide_point, self.explosion_sheet_frames))
        else:
            Globe.MENU.menu_sprites.append(TurretLaser(None, 0, {}, self.image_rect.center, self.angle, self.radius))
            Globe.MENU.menu_sprites.append(Animation(-1, 5, {}, self.explosion_sheet_dims, 2, self.explosion_sheet,
                                                     collide_point, self.explosion_sheet_frames))

        # Adds recoil
        self.desired_angle += random.randint(-self.recoil, self.recoil)

        if not self.display_mode:
            # Collision Detection
            for sprite in Globe.MENU.GAME.SPRITES:
                if "enemy" in sprite.tags:
                    # Checks for hits using the collide point and explosion radius
                    if sprite.hit_check(collide_point, Constants.SCREEN_SIZE[0] / 15):
                        sprite.health -= 1

    def update(self):
        # MOUSE FOLLOW TEST
        # mouse = pygame.mouse.get_pos()
        # cent = self.image_rect.center
        # self.desired_angle = -math.degrees(math.atan2((mouse[1] - cent[1]), (mouse[0] - cent[0])))

        # Makes the current angle continuously approach the desired angle
        if math.fabs(self.angle - self.desired_angle) <= 0.1 and not self.fixated_angle:
            self.angle = self.desired_angle
            self.fixated_angle = True
        elif math.fabs(self.angle - self.desired_angle) > 0.1:
            self.fixated_angle = False
            self.angle += (self.desired_angle - self.angle) / 13

        # Counts down the cool down
        if self.calib_count > 1:
            self.calib_count -= 1
        # Resets the button once cool down wears off
        elif self.calib_count == 1:
            self.calibrate_button.button_state = "static"
            self.calib_count = 0

        if not self.display_mode:
            self.event_handler()

        self.calibrate_button.is_hover(pygame.mouse.get_pos())

    def draw_turret(self, screen):
        self.image, self.image_rect = Object.rotate(self.image_save, self.image_rect, self.angle)

        screen.blit(self.image, self.image_rect)


'''
ENEMY CLASS
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
'''


class Enemy(Object):
    def __init__(self, lifetime, z_order, tags, image, angle, pos, velocity, accel, hitboxes, large_hitbox, health):
        super().__init__(lifetime, z_order, tags)

        self.tags.add("enemy")

        # Saved image that will be used to preserve the quality after transformations
        self.image_save = image

        self.image = copy.copy(self.image_save)
        self.image_rect = self.image.get_rect()
        self.image_rect.center = tuple(pos)

        self.angle = angle
        self.angle_velocity = 0
        self.angle_acceleration = 0

        # The acceleration given by the engine (strength)
        self.engine_acceleration = accel
        # Is the engine currently active
        self.engine_active = False

        # The velocity parameter is given as a single number which is then split into x and y
        self.velocity = []
        self.set_velocity(velocity)

        self.pos = []
        self.set_pos(pos)

        self.acceleration = [0, 0]

        # a set of tuples of hitboxes which represent the hitbox's offset from the center and its radius (offset, rad)
        self.hitboxes = hitboxes
        if self.hitboxes is not None:
            self.hitboxes = set(self.hitboxes)
        # this hitbox is just a radius
        self.large_hitbox = large_hitbox

        self.health = health

        # Death animation variables
        self.opacity = 255
        # Used as a 1 time variable for triggering certain changes on death
        self.init_dead = False
        # detects if explosion spawned
        self.exploded = False

        # Rect.Coordinates to display
        self.display_coords = ()

        # A surface containing a white circle which will be used to spawn the boat trail
        self.trail_surface = pygame.Surface(Constants.cscale(300, 300), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(self.trail_surface, (255, 255, 255), Constants.cscale(150, 150), Constants.cscale(110), 40)

        # Manages delay between trail spawns
        self.trail_delay = 20
        self.trail_delay_count = 10

    def run_sprite(self, screen, update_lock):
        pass

    def set_pos(self, pos):
        self.pos = list(Constants.posscale(pos[0], pos[1]))

    def set_velocity(self, vel):
        self.velocity = [Constants.posscale(vel) * math.cos(math.radians(self.angle)),
                         -Constants.posscale(vel) * math.sin(math.radians(self.angle))]

    def set_acceleration(self, accel):
        self.acceleration = [Constants.posscale(accel) * math.cos(math.radians(self.angle)),
                             -Constants.posscale(accel) * math.sin(math.radians(self.angle))]

    def draw_ship(self, screen):
        self.image, self.image_rect = Object.rotate(self.image_save, self.image_rect, self.angle)

        if self.health <= 0:
            self.image.fill((255, 255, 255, self.opacity if self.opacity >= 0 else 0), None, pygame.BLEND_RGBA_MULT)

        screen.blit(self.image, self.image_rect)

        # Draws rectangular Coordinates
        rendered_text = Constants.COURIER_FONT.render(str(self.display_coords), False, (150, 150, 255))
        screen.blit(rendered_text, (self.image_rect.left + .3 * self.image_rect.w, self.image_rect.top + self.image_rect.h))

        # Draw debug circles of all the hitboxes
        # pygame.draw.circle(screen, (0, 255, 0), self.image_rect.center, int(self.large_hitbox), 1)
        # if self.hitboxes is not None:
        #     for box in self.hitboxes:
        #         pygame.draw.circle(screen, (255, 0, 0), self.get_hitbox_pos(box), box[1], 1)

    def get_hitbox_pos(self, hitbox):
        return (int(self.pos[0] + hitbox[0] * math.cos(math.radians(self.angle))),
                int(self.pos[1] - hitbox[0] * math.sin(math.radians(self.angle))))

    def die(self):
        if not self.init_dead:
            self.init_dead = True
            turn_speed = int(math.sqrt(self.velocity[0] ** 2 + self.velocity[1] ** 2) * 15)
            self.angle_velocity = random.randint(-turn_speed, turn_speed) / 10

        self.opacity -= 1.5

        if self.opacity < 200 and not self.exploded:
            Globe.MENU.GAME.add_sprite(Animation(-1, 5, {}, (9, 9), 2, Constants.EXPLOSION_IMAGE, (-500, -500), 74, binder=self))
            self.exploded = True

        if self.opacity <= 0:
            self.kill = True

    def update(self):
        if self.health <= 0:
            self.engine_active = False

        # Sets acceleration based on whether the engine is active or not
        if self.engine_active:
            self.set_acceleration(self.engine_acceleration)
        else:
            self.acceleration = [0, 0]

        # Angular calculations
        self.angle_velocity += self.angle_acceleration
        self.angle += self.angle_velocity
        self.angle_velocity *= Constants.FRICTION

        # Regular calculations
        self.velocity[0] += self.acceleration[0]
        self.velocity[1] += self.acceleration[1]
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.acceleration[0] *= Constants.FRICTION
        self.acceleration[1] *= Constants.FRICTION

        self.velocity[0] *= Constants.FRICTION
        self.velocity[1] *= Constants.FRICTION

        self.image_rect.centerx = self.pos[0]
        self.image_rect.centery = self.pos[1]

        # Calls death animation
        if self.health <= 0:
            self.die()

        # Calculates display coordinates
        self.display_coords = (int((self.pos[0] / Constants.SCREEN_SIZE[0]) * 900 - 450),
                               int(((Constants.SCREEN_SIZE[1] - self.pos[1]) / Constants.SCREEN_SIZE[1]) * 900 - 450))

        # If the boat's speed is above a certain value, trail will spawn
        print("Scaled velocity", self.velocity[0], Constants.posscale(0.1))
        if math.fabs(self.velocity[0]) > Constants.posscale(0.1) or math.fabs(self.velocity[1]) > Constants.posscale(0.1):
            self.trail_delay_count += 1
            print("hey")
            if self.trail_delay_count > self.trail_delay:
                self.trail_delay_count = 0
                Globe.MENU.GAME.add_sprite(InflateSurface(110, -2000, {}, self.trail_surface, 0.01, .3, 100,
                                                          copy.copy(self.pos), fade=True, delay_inflation=10))

    # Checks collision with another circular hitbox against all the hitboxes of this enemy
    def hit_check(self, pos, radius):
        # If there are no hitboxes available then check against the big one
        if self.hitboxes is None:
            if Constants.distance(self.image_rect.center, pos) < radius + self.large_hitbox:
                return True
            else:
                return False

        else:
            # Checks for collision against the large encompassing hitbox to optimize
            if Constants.distance(self.image_rect.center, pos) < radius + self.large_hitbox:
                for box in self.hitboxes:
                    if Constants.distance(self.get_hitbox_pos(box), pos) < radius + box[1]:
                        return True
            return False



'''
JETSHIP CHARGER CLASS
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
```````````````````````````````````````
'''


class JetshipCharger(Enemy):
    def __init__(self, lifetime, z_order, tags, image, angle, pos, velocity, acceleration, health):
        super().__init__(lifetime, z_order, tags, image, angle, pos, velocity, acceleration, None, (15 / 340) * Constants.SCREEN_SIZE[0], health)

        self.engine_active = True

    def run_sprite(self, screen, update_lock):
        if not update_lock:
            self.update()
        self.draw_ship(screen)


class Buoy(Enemy):
    def __init__(self, lifetime, z_order, tags, pos, health):
        super().__init__(lifetime, z_order, tags, Constants.BUOY_IMAGE, 0, pos, 0, 0, None, Constants.posscale(40), health)

        # Used for sine function for waving
        self.time = 0

        self.original_rect = copy.deepcopy(self.image_rect)
        self.original_center = copy.copy(self.image_rect.center)

        self.tilt_angle = 5

    def run_sprite(self, screen, update_lock):
        if not update_lock:
            self.update()
            self.time += 1
        self.draw_ship(screen)

    def die(self):
        if not self.init_dead:
            self.init_dead = True
            self.tilt_angle = 50

        self.tilt_angle -= .08
        self.opacity -= 1.5

        if self.opacity <= 0:
            self.kill = True

    def draw_ship(self, screen):
        #self.image, self.image_rect = Object.rotate(self.image_save, self.image_rect, self.angle)
        r = self.original_rect.h / 2
        rotate_point = (self.original_center[0], self.original_center[1] + self.original_rect.h / 2)
        angle = (self.tilt_angle * math.sin(.05 * self.time) + 90)
        center = (rotate_point[0] + r * math.cos(math.radians(angle)), rotate_point[1] - r * math.sin(math.radians(angle)))
        self.image = pygame.transform.rotate(self.image_save, self.tilt_angle * math.sin(.05 * self.time))
        self.image_rect = self.image.get_rect(center=center)

        if self.health <= 0:
            self.image.fill((255, 255, 255, self.opacity if self.opacity >= 0 else 0), None, pygame.BLEND_RGBA_MULT)

        screen.blit(self.image, self.image_rect)

        # DEBUG SHAPES
        #pygame.draw.circle(screen, (0, 255, 0), [int(x) for x in rotate_point], 3)
        #pygame.draw.circle(screen, (0, 0, 255), self.image_rect.center, 3)
        #pygame.draw.rect(screen, (0, 255, 0), self.image_rect, 1)

        # Draws rectangular Coordinates
        rendered_text = Constants.COURIER_FONT.render(str(self.display_coords), False, (150, 150, 255))
        screen.blit(rendered_text,
                    (self.image_rect.left + .3 * self.image_rect.w, self.image_rect.top + self.image_rect.h))

        # Draw debug circles of all the hitboxes
        # pygame.draw.circle(screen, (0, 255, 0), self.image_rect.center, int(self.large_hitbox), 1)
        # if self.hitboxes is not None:
        #     for box in self.hitboxes:
        #         pygame.draw.circle(screen, (255, 0, 0), self.get_hitbox_pos(box), box[1], 1)