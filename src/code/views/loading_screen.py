# loading_screen.py
"""Loading screen with spinner animation and progress bar."""

import pygame
from utils import draw_progress_bar


class LoadingScreen:
    """Handles the loading screen with transition effects."""

    def __init__(self, design_width, design_height):
        """Initializes the loading screen with specific dimensions."""
        self.design_width = design_width
        self.design_height = design_height
        self.progress = 0
        self.alpha = 0
        self.fade_speed = 8
        self.active = True

        self.overlay = pygame.Surface((design_width, design_height), pygame.SRCALPHA)
        self.font = pygame.font.Font("src/assets/fonts/SpecialElite-Regular.ttf", 24)
        self.loading_text = self.font.render("Loading...", True, (255, 255, 255))
        self.spinner_angle = 0


    def update_progress(self, progress):
        """Updates the loading progress."""
        self.progress = progress


    def update_fade(self):
        """Updates the fade-in/fade-out effect."""
        if self.active and self.alpha < 255:
            self.alpha = min(self.alpha + self.fade_speed, 255)
        elif not self.active and self.alpha > 0:
            self.alpha = max(self.alpha - self.fade_speed, 0)


    def draw_spinner(self, screen):
        """Draws an animated spinner."""
        self.spinner_angle = (self.spinner_angle + 5) % 360
        spinner = pygame.Surface((40, 40), pygame.SRCALPHA)
        pygame.draw.arc(spinner, (255, 255, 255), (0, 0, 40, 40), 0, 300, 5)
        rotated = pygame.transform.rotate(spinner, self.spinner_angle)
        screen.blit(rotated, (self.design_width//2 - 20, self.design_height//2 + 30))


    def draw(self, screen):
        """Draws the loading screen."""
        self.overlay.fill((0, 0, 0, self.alpha))
        screen.blit(self.overlay, (0, 0))
        
        if self.alpha == 255:
            self.alpha = max(0, min(255, int(self.alpha)))
            screen.fill((0, 0, 0))
            text_rect = self.loading_text.get_rect(center=(self.design_width//2, self.design_height//2 - 50))
            screen.blit(self.loading_text, text_rect)
            draw_progress_bar(screen, self.progress, (self.design_width//2 - 100, self.design_height//2, 200, 20))
            self.draw_spinner(screen)

        # Retornar True cuando la transición haya terminado
        return self.alpha == 0 and not self.active