"""Button class for interactive UI elements."""

import pygame
from constants import font_path, font_sizes, font_colors


class Button:
    """Represents a clickable button with hover effects."""

    def __init__(self, text, x, y, width, height, on_click=None, 
                 font=None, font_size=None, text_color=None, bg_color=None, 
                 hover_color=None, border_radius=15, border_width=2, image_path=None,
                 hover_image_path=None, border_size=12, use_9slice=True, disabled=False):
        """Initializes the button with text, position, and behavior."""
        self.text = text
        self.original_x = x
        self.original_y = y
        self.original_width = width
        self.original_height = height
        self.on_click = on_click
        self.rect = pygame.Rect(x, y, width, height)
        self.hovered = False
        self.image_path = image_path
        self.image = None
        self.scaled_image = None
        self.hover_image = None
        self.border_size = border_size 
        self.use_9slice = use_9slice
        self.disabled = disabled
        
        if self.image_path:
            self.load_image()

    def load_image(self):
        """Loads the button's background image."""
        try:
            self.image = pygame.image.load(self.image_path).convert_alpha()
            self.scale_image()
            self.create_hover_image()
        except pygame.error as e:
            print(f"Error loading image: {e}")
            self.image = None

    def create_hover_image(self):
        """Creates a brighter version of the image for hover effect."""
        if not self.image:
            return
            
        hover_img = self.image.copy()
        
        for y in range(hover_img.get_height()):
            for x in range(hover_img.get_width()):
                r, g, b, a = hover_img.get_at((x, y))
                r = min(r + 30, 255)
                g = min(g + 30, 255)
                b = min(b + 30, 255)
                hover_img.set_at((x, y), (r, g, b, a))
        
        self.hover_image = hover_img
        self.scale_hover_image()

    def resize(self, scale_x, scale_y):
        """Adjusts the button size and position when resized."""
        self.rect.x = self.original_x * scale_x
        self.rect.y = self.original_y * scale_y
        self.rect.width = self.original_width * scale_x
        self.rect.height = self.original_height * scale_y

        if self.image:
            self.scale_image()
            self.scale_hover_image()

    def scale_image(self):
        """Scales the image to fit the button size."""
        if not self.image:
            return
            
        if self.use_9slice and self.image.get_width() >= self.border_size * 2 and self.image.get_height() >= self.border_size * 2:
            self.scaled_image = self.scale_9slice(self.image).convert_alpha()
        else:
            self.scaled_image = pygame.transform.scale(self.image, (self.rect.width, self.rect.height)).convert_alpha()

    def scale_hover_image(self):
        """Scales the hover image to fit the button size."""
        if not self.hover_image:
            return
            
        if self.use_9slice and self.hover_image.get_width() >= self.border_size * 2 and self.hover_image.get_height() >= self.border_size * 2:
            self.scaled_hover_image = self.scale_9slice(self.hover_image)
        else:
            self.scaled_hover_image = pygame.transform.scale(self.hover_image, (self.rect.width, self.rect.height))

    def scale_9slice(self, source_image):
        """Scales the image using 9-slice technique to preserve corners and borders."""
        result = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)

        orig_width = source_image.get_width()
        orig_height = source_image.get_height()
        
        border = min(self.border_size, orig_width // 2, orig_height // 2)

        corner_tl = source_image.subsurface((0, 0, border, border))
        corner_tr = source_image.subsurface((orig_width - border, 0, border, border))
        corner_bl = source_image.subsurface((0, orig_height - border, border, border))
        corner_br = source_image.subsurface((orig_width - border, orig_height - border, border, border))
        
        border_t = source_image.subsurface((border, 0, orig_width - 2 * border, border))
        border_b = source_image.subsurface((border, orig_height - border, orig_width - 2 * border, border))
        border_l = source_image.subsurface((0, border, border, orig_height - 2 * border))
        border_r = source_image.subsurface((orig_width - border, border, border, orig_height - 2 * border))

        center = source_image.subsurface((border, border, orig_width - 2 * border, orig_height - 2 * border))

        scaled_border_t = pygame.transform.scale(border_t, (self.rect.width - 2 * border, border))
        scaled_border_b = pygame.transform.scale(border_b, (self.rect.width - 2 * border, border))
        scaled_border_l = pygame.transform.scale(border_l, (border, self.rect.height - 2 * border))
        scaled_border_r = pygame.transform.scale(border_r, (border, self.rect.height - 2 * border))
        scaled_center = pygame.transform.scale(center, (self.rect.width - 2 * border, self.rect.height - 2 * border))

        result.blit(corner_tl, (0, 0))
        result.blit(corner_tr, (self.rect.width - border, 0))
        result.blit(corner_bl, (0, self.rect.height - border))
        result.blit(corner_br, (self.rect.width - border, self.rect.height - border))

        result.blit(scaled_border_t, (border, 0))
        result.blit(scaled_border_b, (border, self.rect.height - border))
        result.blit(scaled_border_l, (0, border))
        result.blit(scaled_border_r, (self.rect.width - border, border))

        result.blit(scaled_center, (border, border))
        return result

    def draw(self, screen):
        """Draws the button on the screen."""
        if self.scaled_image:
            if self.hovered and hasattr(self, 'scaled_hover_image') and not self.disabled:
                screen.blit(self.scaled_hover_image, self.rect)
            else:
                screen.blit(self.scaled_image, self.rect)
        else:
            color = (150, 150, 150) if self.disabled else ((200, 200, 200) if not self.hovered else (255, 255, 255))
            pygame.draw.rect(screen, color, self.rect)

        font_size = min(font_sizes["medium"], int(self.rect.height * 0.6))
        font = pygame.font.Font(font_path, font_size)
        
        text_color = (100, 100, 100) if self.disabled else font_colors["button"]
        text_surface = font.render(self.text, True, text_color)
        
        padding = max(10, int(self.rect.width * 0.1))  # 10px or 10% of width, whichever is larger
        text_rect = text_surface.get_rect(
            center=(self.rect.centerx, self.rect.centery)
        )
        
        screen.blit(text_surface, text_rect)

    def check_click(self, mouse_pos):
        """Checks if the button has been clicked."""
        if self.disabled:
            return  # Ignore clicks on disabled buttons
            
        if self.rect.collidepoint(mouse_pos) and self.on_click:
            self.on_click()
            return True
        return False

    def check_hover(self, mouse_pos):
        """Checks if the mouse is hovering over the button."""
        was_hovered = self.hovered
        self.hovered = self.rect.collidepoint(mouse_pos) and not self.disabled
        return was_hovered != self.hovered