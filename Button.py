import pygame


class Button:
    def __init__(self, top_left_corner, size, image, box=False, border_color=(0, 0, 0), text_color=(40, 40, 40),
                 fill_color=(255, 255, 255), text="", border_thickness=0, font=None):
        # Position of top left corner of button.
        self.top_left = top_left_corner

        self.text = text
        # Width/height of image and the loaded image.
        self.size = size
        self.image = None
        if image is not None:
            self.image = pygame.transform.scale(image, (size[0], size[1] * 3))

        # Image contains 2 states of the button. These 2 surfaces will hold each state.
        self.static = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.hover = pygame.Surface(self.size, pygame.SRCALPHA, 32)
        self.pressed = pygame.Surface(self.size, pygame.SRCALPHA, 32)

        if not box:
            self.static.blit(self.image, (0, 0))
            self.hover.blit(self.image, (0, -self.size[1]))
            self.pressed.blit(self.image, (0, -2 * self.size[1]))
        else:
            self.static.fill(border_color)
            pygame.draw.rect(self.static, fill_color, (border_thickness, border_thickness,
                                                       self.size[0] - 2 * border_thickness,
                                                       self.size[1] - 2 * border_thickness))
            if font is not None:
                rendered_text = font.render(text, True, text_color)
                rect = rendered_text.get_rect()
                rect.center = (self.size[0] / 2, self.size[1] / 2)
                self.static.blit(rendered_text, rect)

                self.hover.blit(self.static, (0, 0))

        self.button_rect = self.static.get_rect()
        self.button_rect.center = top_left_corner[0] + size[0] / 2, top_left_corner[1] + size[1] / 2

        self.button_state = "static"

    def draw(self, screen):
        if self.button_state == "pressed":
            screen.blit(self.pressed, self.top_left)
        else:
            screen.blit(self.hover if self.button_state == "hover" else self.static, self.top_left)

    def is_hover(self, pos):
        if not self.button_state == "pressed":
            self.button_state = "hover" if pygame.Rect(self.top_left, self.size).collidepoint(pos) else "static"

    def is_clicked(self, pos):
        return pygame.Rect(self.top_left, self.size).collidepoint(pos)
