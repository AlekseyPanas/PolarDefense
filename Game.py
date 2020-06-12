import Sprite
import Constants
import random
import Globe
import pygame
import Button


class Game:
    def __init__(self, level_json):
        self.start_button = Button.Button(Constants.cscale(345, 300), Constants.cscale(210, 70), Constants.START_BUTTON)
        self.menu_button = Button.Button(Constants.cscale(345, 380), Constants.cscale(210, 70), Constants.MENU_BUTTON)

        self.json = level_json

        self.SPRITES = []
        self.delete_sprites = set([])

        # Since you shouldn't add sprites during iteration, they are queued to be added at the end of the loop
        self.sprite_queue = set([])

        # Loss conditions for this level:
        # "offscreen" = if an enemy has gone off screen, you lose
        self.loss_types = set([])

        # Pauses game
        self.update_lock = True
        # Determines if the level is in a start game state
        self.started = False

        # Determines when a loss condition has been met
        self.game_over = False
        # Allows for any animations before level reset
        self.game_over_timer = 300
        # When true, Menu resets the level back to the start
        self.end_game = False

        # Set to true when the level has been beaten
        self.is_win = False
        # Gives time for victory popups
        self.win_count = 300
        # Tells the menu to move to the next level
        self.set_complete = False

        self.exit_level = False

        # 1 time lock variable for spawning inflating game over text or win text
        self.spawned_inflations = False

        self.add_sprite(Sprite.Turret(None, 999, {}, (Constants.SCREEN_SIZE[0] / 2, Constants.SCREEN_SIZE[1] / 2),
                                      (0, int(0.022 * Constants.SCREEN_SIZE[1])), 80, 40))

        self.load_level()

    def load_level(self):
        # loads enemies. Enemy type strings include:
        # "jet_charger" = Jet Charger
        # "buoy" = Buoy
        for enemy in self.json["enemies"]:
            if enemy["type"] == "jet_charger":
                self.add_sprite(Sprite.JetshipCharger(None, -5, {}, Constants.JET_CHARGER_IMAGE, enemy["angle"],
                                                      enemy["pos"], enemy["velocity"], enemy["acceleration"],
                                                      enemy["health"]))
            elif enemy["type"] == "buoy":
                self.add_sprite(Sprite.Buoy(None, -5, {}, enemy["pos"], enemy["health"]))

        self.loss_types = set(self.json["loss_types"])

    def add_sprite(self, sprite):
        self.sprite_queue.add(sprite)

    def event_handler(self):
        for event in Globe.events:
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_ESCAPE and self.started:
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                        self.exit_level = True
            elif event.type == pygame.MOUSEBUTTONUP and not self.started:
                if self.start_button.is_clicked(event.pos):
                    self.started = True
                    self.update_lock = False
                if self.menu_button.is_clicked(event.pos):
                    self.exit_level = True

    def run_game(self, screen):
        Game.draw_background(screen)

        self.event_handler()

        self.manage_sprites(screen)

        if not self.started:
            rendered_text = Constants.VERY_BIGBOI_FONT.render("Level: " + str(self.json["id"]), True, (255, 0, 255))
            rect = rendered_text.get_rect()
            rect.center = Constants.cscale(450, 200)
            screen.blit(rendered_text, rect)

            screen.blit(Constants.START_BAR_IMAGE, Constants.cscale(0, 250))

            self.start_button.is_hover(pygame.mouse.get_pos())
            self.start_button.draw(screen)
            self.menu_button.is_hover(pygame.mouse.get_pos())
            self.menu_button.draw(screen)

        # Manages game over stuff
        gameover_output = self.check_game_over()
        if gameover_output > -1 and not self.game_over and not self.is_win:
            self.game_over = True
            text = "You lost"
            if gameover_output == 0:
                text = "You let an enemy escape!"
            elif gameover_output == 1:
                text = "You got blown up!"
            elif gameover_output == 2:
                text = "You took too long!"
            self.spawned_inflations = True
            self.add_sprite(Sprite.InflateSurface(300, 2000, {}, Constants.GAMEOVER_IMAGE, .01, 3, 50,
                                                    Constants.cscale(450, 150)))
            self.add_sprite(Sprite.InflateSurface(300, 2000, {},
                                                    Constants.BIGBOI_FONT.render(text, True,
                                                                                (255, 0, 0)), .01, 1.5, 50,
                                                    Constants.cscale(450, 250)))
        if self.game_over:
            self.game_over_timer -= 1
        if self.game_over_timer <= 0:
            self.end_game = True

        # Manages win detection
        if self.check_win() and not self.game_over and not self.is_win:
            self.is_win = True
            self.add_sprite(Sprite.InflateSurface(300, 2000, {}, Constants.LEVEL_COMPLETE_IMAGE, .01, 3, 50,
                                                  Constants.cscale(450, 150)))
        if self.is_win:
            self.win_count -= 1
        if self.win_count <= 0:
            self.set_complete = True

    def check_win(self):
        if not len([sprite for sprite in self.SPRITES if "enemy" in sprite.tags and sprite.health > 0]):
            return True
        else:
            return False

    def check_game_over(self):
        # Returns code depending on game over reason
        # -1 = no game over, 0 = offscreen, 1 = health, 2 = time
        return_code = -1

        if "offscreen" in self.loss_types:
            for sprite in self.SPRITES:
                if "enemy" in sprite.tags:
                    if sprite.health > 0:
                        if sprite.pos[0] + sprite.large_hitbox <= 0 or sprite.pos[0] - sprite.large_hitbox >= Constants.SCREEN_SIZE[0] or sprite.pos[1] + sprite.large_hitbox <= 0 or sprite.pos[1] - sprite.large_hitbox >= Constants.SCREEN_SIZE[1]:
                            return_code = 0

        return return_code

    def manage_sprites(self, screen):
        # Runs sprites
        for sprite in self.SPRITES:
            sprite.run_sprite(screen, self.update_lock)

            # Deletes killed sprites
            if sprite.kill:
                self.delete_sprites.add(sprite)
            # Manages lifetime
            if sprite.lifetime is not None and not self.update_lock:
                if sprite.lifetime <= 0:
                    self.delete_sprites.add(sprite)
                sprite.lifetime -= 1

        # Removes dead sprites
        for sprite in self.delete_sprites:
            if sprite in self.SPRITES:
                self.SPRITES.remove(sprite)

        # Add new sprites
        for sprite in self.sprite_queue:
            self.SPRITES.append(sprite)
        if len(self.sprite_queue):
            self.SPRITES = sorted(self.SPRITES, key=lambda spr: spr.z_order)
            self.sprite_queue = set([])

    @staticmethod
    def draw_background(screen):
        screen.blit(Constants.OCEAN_IMAGE, (0, 0))
        screen.blit(Constants.ISLAND_IMAGE, ((Constants.SCREEN_SIZE[0] / 2) - (Constants.ISLAND_IMAGE.get_width() / 2),
                                             (Constants.SCREEN_SIZE[0] / 2) - (
                                                         Constants.ISLAND_IMAGE.get_height() / 2)))
