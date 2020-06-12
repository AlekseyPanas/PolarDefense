import Game
import Constants
import Button
import pygame
import Globe
import Sprite
from PIL import Image, ImageFilter
import random
import copy


# This class manages the entire game. Manages level selection, tutorial screens, etc
class Menu:
    def __init__(self):
        # Game object which runs the actual game
        self.GAME = Game.Game()

        # String state of menu. Determines what the menu displays
        self.menu_state = "tutor"

        # Dictionary of corresponding variables
        self.init_vars = {"tutor": False, "game": False, "main": False}

        # TUTOR VARS
        # BUTTONS ARE PLACEHOLDERS
        self.skip_button = Button.Button(Constants.cscale(650, 840), Constants.cscale(100, 50), Constants.SKIP_BUTTON)
        self.next_button = Button.Button(Constants.cscale(760, 840), Constants.cscale(100, 50), Constants.NEXT_BUTTON)
        self.back_button = Button.Button(Constants.cscale(540, 840), Constants.cscale(100, 50), Constants.BACK_BUTTON)

        self.no_button = Button.Button(Constants.cscale(500, 520), Constants.cscale(100, 50), Constants.NO_BUTTON)
        self.yes_button = Button.Button(Constants.cscale(300, 520), Constants.cscale(100, 50), Constants.YES_BUTTON)

        self.page_index = None
        self.pages = (Constants.TUT_1_IMG, Constants.TUT_2_IMG, Constants.TUT_3_IMG, Constants.TUT_4_IMG,
                      Constants.TUT_5_IMG, Constants.TUT_6_IMG, Constants.TUT_7_IMG)
        # Confirm skip
        self.confirm_popup = False

        self.popup_shadow = Constants.create_shadow(Constants.cscale(500, 300), (100, 0, 100))
        self.popup_text = Constants.BIGBOI_FONT.render("ARE YOU SURE?", True, (0, 0, 0))
        self.popup_text_rect = self.popup_text.get_rect()
        self.popup_text_rect.center = Constants.cscale(450, 400)
        self.popup_surface = pygame.Surface(Constants.cscale(500, 300), pygame.SRCALPHA, 32)
        self.popup_surface.convert_alpha()
        # Draws popup box
        pygame.draw.rect(self.popup_surface, (255, 0, 255, 250), Constants.cscale(0, 0, 500, 300))
        pygame.draw.rect(self.popup_surface, (255, 255, 255, 150), Constants.cscale(10, 10, 480, 280))

        # TRUMPS WALL:
        # ============================
        # ============================

        # Main Menu variables
        # Blurred images
        self.ocean = Constants.blur_surface(copy.copy(Constants.OCEAN_IMAGE), 7).convert_alpha()
        self.island = Constants.blur_surface(copy.copy(Constants.ISLAND_IMAGE), 5).convert_alpha()
        self.explosion = Constants.blur_surface(copy.copy(Constants.EXPLOSION_IMAGE), 5).convert_alpha()
        self.turret = Constants.blur_surface(copy.copy(Constants.TURRET_IMAGE), 3).convert_alpha()

        self.turret = Sprite.Turret(None, 999, {}, (Constants.SCREEN_SIZE[0] / 2, Constants.SCREEN_SIZE[1] / 2),
                                    (0, int(0.022 * Constants.SCREEN_SIZE[1])), 80, 100, display_mode=True,
                                    explosion_sheet=self.explosion, turret_image=self.turret)
        self.menu_sprites = []
        self.menu_remove_sprites = []

        # Sets island to be drawn at center
        self.island_rect = Constants.ISLAND_IMAGE.get_rect()
        self.island_rect.center = Constants.cscale(450, 450)

        # The delay between shots in the menu and the counter for the delay
        self.shoot_counter = None
        self.shoot_delay = None

        # Menu Buttons
        self.levels_button = Button.Button(Constants.cscale(50, 300), Constants.cscale(200, 100), Constants.LEVELS_BUTTON)
        self.quit_button = Button.Button(Constants.cscale(350, 700), Constants.cscale(200, 100), Constants.QUIT_BUTTON)
        self.tutorial_button = Button.Button(Constants.cscale(650, 300), Constants.cscale(200, 100), Constants.TUTORIAL_BUTTON)

        self.back_button2 = Button.Button(Constants.cscale(50, 250), Constants.cscale(100, 50), Constants.BACK_BUTTON)

        # Substates of the main menu
        # 0 = main, 1 = levels
        self.menu_substate = 0

    def run_menu(self, screen):
        if self.menu_state == "tutor":
            self.run_tutorial(screen)
        elif self.menu_state == "game":
            self.GAME.run_game(screen)
        elif self.menu_state == "main":
            self.run_main_menu(screen)

        self.check_vars()

    def check_vars(self):
        for var in self.init_vars:
            if not var == self.menu_state:
                self.init_vars[var] = False

    def run_main_menu(self, screen):
        # 1 time instantiation
        if not self.init_vars["main"]:
            self.shoot_counter = 0
            self.shoot_delay = 100
            self.menu_substate = 0
            self.menu_sprites = []
            self.menu_remove_sprites = []
            self.init_vars["main"] = True

        # Run Blurred game
        self.shoot_counter += 1
        if self.shoot_counter >= self.shoot_delay:
            self.turret.radius = random.randint(200, 450)
            self.turret.shoot()
            self.shoot_counter = 0
            self.shoot_delay = random.randint(100, 300)
            self.turret.desired_angle = random.randint(-400, 400)

        # Draw Blurred image
        screen.blit(self.ocean, (0, 0))
        screen.blit(self.island, self.island_rect)

        for sprite in self.menu_sprites:
            if "Laser" in sprite.tags:
                sprite.color = (100, 90, 150)
            sprite.run_sprite(screen, False)
            sprite.lifetime -= 1
            if sprite.lifetime <= 0:
                self.menu_remove_sprites.append(sprite)

        for sprite in self.menu_remove_sprites:
            if sprite in self.menu_sprites:
                self.menu_sprites.remove(sprite)
        self.menu_remove_sprites = []

        self.turret.run_sprite(screen, False)

        ##### The actual menu
        ### ================
        rect = Constants.LOGO_IMAGE.get_rect()
        rect.center = Constants.cscale(450, 100)
        screen.blit(Constants.LOGO_IMAGE, rect)

        if self.menu_substate == 0:
            self.levels_button.is_hover(pygame.mouse.get_pos())
            self.quit_button.is_hover(pygame.mouse.get_pos())
            self.tutorial_button.is_hover(pygame.mouse.get_pos())

            self.levels_button.draw(screen)
            self.quit_button.draw(screen)
            self.tutorial_button.draw(screen)

            for event in Globe.events:
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.levels_button.is_clicked(event.pos):
                        self.menu_substate = 1
                    if self.quit_button.is_clicked(event.pos):
                        Globe.running = False
                    if self.tutorial_button.is_clicked(event.pos):
                        self.menu_state = "tutor"
        else:
            self.back_button2.is_hover(pygame.mouse.get_pos())
            self.back_button2.draw(screen)

            for event in Globe.events:
                if event.type == pygame.MOUSEBUTTONUP:
                    if self.back_button2.is_clicked(event.pos):
                        self.menu_substate = 0

    def run_tutorial(self, screen):
        # 1 time instantiation
        if not self.init_vars["tutor"]:
            self.page_index = 0
            self.confirm_popup = False
            self.init_vars["tutor"] = True

        # Events
        self.skip_button.is_hover(pygame.mouse.get_pos())
        self.next_button.is_hover(pygame.mouse.get_pos())
        self.back_button.is_hover(pygame.mouse.get_pos())

        # Checks for button presses
        for event in Globe.events:
            if event.type == pygame.MOUSEBUTTONUP:
                if not self.confirm_popup:
                    if self.skip_button.is_clicked(event.pos):
                        self.confirm_popup = True
                    if self.next_button.is_clicked(event.pos):
                        self.page_index += 1
                        if self.page_index > len(self.pages) - 1:
                            self.menu_state = "main"
                            return
                    elif self.back_button.is_clicked(event.pos):
                        self.page_index -= 1
                        if self.page_index < 0:
                            self.page_index = 0
                else:
                    if self.no_button.is_clicked(event.pos):
                        self.confirm_popup = False
                    if self.yes_button.is_clicked(event.pos):
                        # SKIP TUTOR
                        self.menu_state = "main"

        # Draws page
        screen.blit(self.pages[self.page_index], (0, 0))

        # Draws popup if applicable
        if self.confirm_popup:
            screen.blit(self.popup_shadow, Constants.cscale(190, 290))
            # Draws shadow
            screen.blit(self.popup_surface, Constants.cscale(200, 300))
            # Draws text
            screen.blit(self.popup_text, self.popup_text_rect)
            self.popup_text.get_rect()
            # Draw buttons and hover them
            self.no_button.draw(screen)
            self.yes_button.draw(screen)
            self.no_button.is_hover(pygame.mouse.get_pos())
            self.yes_button.is_hover(pygame.mouse.get_pos())

        # Draws buttons
        self.skip_button.draw(screen)
        self.next_button.draw(screen)
        self.back_button.draw(screen)
