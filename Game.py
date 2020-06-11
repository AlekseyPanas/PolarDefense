import Sprite
import Constants


class Game:
    def __init__(self):
        self.SPRITES = []
        self.delete_sprites = []

        # Since you shouldn't add sprites during iteration, they are queued to be added at the end of the loop
        self.sprite_queue = []

        self.add_sprite(Sprite.Turret(None, 999, (Constants.SCREEN_SIZE[0] / 2, Constants.SCREEN_SIZE[1] / 2),
                                      (0, int(0.022 * Constants.SCREEN_SIZE[1])), 80, 40))

    def add_sprite(self, sprite):
        self.sprite_queue.append(sprite)

    def run_game(self, screen):
        Game.draw_background(screen)

        # Runs sprites
        for sprite in self.SPRITES:
            sprite.run_sprite(screen)

            # Deletes killed sprites
            if sprite.kill:
                self.delete_sprites.append(sprite)
            # Manages lifetime
            if sprite.lifetime is not None:
                if sprite.lifetime <= 0:
                    self.delete_sprites.append(sprite)
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
            self.sprite_queue = []

    @staticmethod
    def draw_background(screen):
        screen.blit(Constants.OCEAN_IMAGE, (0, 0))
        screen.blit(Constants.ISLAND_IMAGE, ((Constants.SCREEN_SIZE[0] / 2) - (Constants.ISLAND_IMAGE.get_width() / 2),
                                             (Constants.SCREEN_SIZE[0] / 2) - (
                                                         Constants.ISLAND_IMAGE.get_height() / 2)))
