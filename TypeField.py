import pygame
import Constants


class Field:
    def __init__(self, pos, length, font, image, disable_negative, minimum_value):
        # Draw pos of field
        self.pos = pos
        # Is the type field selected
        self.selected = False
        # The text in the type field
        self.text = ""
        # A surface that will contain the rendered text
        self.rendered_text = None
        # The position where the cursor is
        self.cursor_index = -1
        self.cursor_pos = 0
        # Counter used for the cursor blinking
        self.blink_count = 0
        # Position of text
        self.text_pos = 10
        # image
        self.image = image
        # font
        self.font = font
        # dimensions of the type field
        self.length = length
        self.height = self.font.get_height() + (self.font.get_height() / 12)
        # Disables negative values for certain fields
        self.disable_negative = disable_negative
        # All the symbols the user may type
        self.allowed_symbols = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "."}
        if not self.disable_negative:
            self.allowed_symbols.add("-")

        # The smallest value that can be entered into the field.
        self.minimum_value = minimum_value

        # The surface that everything will be blitted on
        self.surface = pygame.Surface((length, self.height), pygame.SRCALPHA, 32)
        self.text_surface = pygame.Surface((length - 6, self.height), pygame.SRCALPHA, 32)
        # Glass type field image
        self.image = pygame.transform.scale(self.image, (int(length), int(self.height)))

        # pre-rendered texts for certain conditions
        self.zero_rendered = self.font.render("0", False, (0, 255, 0))
        self.negative_rendered = self.font.render("-0", False, (0, 255, 0))

        # Used to adjust cursor for the decimal
        self.decimal_adjust = False

    def draw_handler(self, screen):
        if self.selected:
            self.blink_count += 1

        self.surface.fill((255, 255, 255, 0))
        self.text_surface.fill((255, 255, 255, 0))

        # Draws text
        self.rendered_text = self.font.render(self.text, True, (0, 255, 0))
        if self.text == "":
            self.text_surface.blit(self.zero_rendered, (self.text_pos, -2))
        elif self.text == "-":
            self.text_surface.blit(self.negative_rendered, (self.text_pos, -2))
        self.text_surface.blit(self.rendered_text, (self.text_pos, -2))
        self.surface.blit(self.text_surface, (3, 0))

        # Finds cursor position based on index
        self.cursor_pos = self.font.render(self.text[:self.cursor_index + 1], True, (0, 0, 0)).get_width()

        # Draws glass typing field image
        self.surface.blit(self.image, (0, 0))

        # Draws cursor
        if self.blink_count % 40 < 20 and self.selected:
            pygame.draw.line(self.surface, (200, 0, 0), ((self.text_pos - 1) + self.cursor_pos + ((2 / 900) * Constants.SCREEN_SIZE[0]), (1 / 6) * self.height),
                             ((self.text_pos - 1) + self.cursor_pos + ((2 / 900) * Constants.SCREEN_SIZE[0]), self.height - (1 / 6) * self.height), 2)

        # Determines if a shift of text is needed
        if (self.text_pos - 1) + self.cursor_pos < 0:
            self.text_pos += (0 - ((self.text_pos - 1) + self.cursor_pos)) + 10
        elif (self.text_pos - 1) + self.cursor_pos > self.length:
            self.text_pos += (self.length - ((self.text_pos - 1) + self.cursor_pos)) - 10

        screen.blit(self.surface, self.pos)

    def event_handler(self, event):
        # Checks to see if the box was clicked which causes it to become selected
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pos[0] < event.pos[0] < self.pos[0] + self.length and self.pos[1] < event.pos[1] < self.pos[1] + self.height:
                self.selected = True
            else:
                self.selected = False
        # Key presses
        elif self.selected and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_index > -1:
                    self.text = self.text[:self.cursor_index] + self.text[self.cursor_index + 1:]
                    # Shifts cursor left
                    self.cursor_index -= 1

            elif event.key == pygame.K_ESCAPE:
                self.text = ""
                self.cursor_index = -1

            # Checks if arrows were pressed and shifts cursor accordingly
            elif event.key == pygame.K_LEFT and self.cursor_index > -1:
                self.cursor_index -= 1
            elif event.key == pygame.K_RIGHT and self.cursor_index < len(self.text) - 1:
                self.cursor_index += 1

            elif len(event.unicode) > 0 and event.unicode in self.allowed_symbols:
                if not(event.unicode == "." and "." in self.text) and not (event.unicode == "-" and not (self.cursor_index == -1)) and not (event.unicode == "-" and "-" in self.text):
                    self.text = self.text[:self.cursor_index + 1] + event.unicode + self.text[self.cursor_index + 1:]
                    # Shifts cursor to right
                    self.cursor_index += 1

        if self.text == "." and not self.decimal_adjust:
            self.text = "0."
            self.cursor_index = 1
            self.decimal_adjust = True
        else:
            self.decimal_adjust = False

        if self.text == "0":
            self.text = ""
            self.cursor_index = -1

        # Ensures the minimum value is enforced as long as the field is not selected
        if self.minimum_value is not None:
            if self.text == "-" or self.text == "":
                val = 0
            else:
                val = float(self.text)
            if (not self.selected) and val < self.minimum_value:
                self.text = str(self.minimum_value)
                self.cursor_index = len(str(self.minimum_value)) - 1
