import pygame


class Button:
    def __init__(self, text, x, y, width, height, on_click):
        self.text = text
        self.original_x = x
        self.original_y = y
        self.original_width = width
        self.original_height = height
        self.on_click = on_click
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False


    def resize(self, scale_x, scale_y):
        """ Adjust the button size and position """
        self.rect.x = self.original_x * scale_x
        self.rect.y = self.original_y * scale_y
        self.rect.width = self.original_width * scale_x
        self.rect.height = self.original_height * scale_y


    def check_hover(self, mouse_pos):
        """ Verify if the mouse is hovering over the button """
        self.hovered = self.rect.collidepoint(mouse_pos)


    def draw(self, screen):
        """ Draw the button on the screen """
        color = (200, 200, 200) if not self.hovered else (255, 255, 255)
        pygame.draw.rect(screen, color, self.rect)

        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)