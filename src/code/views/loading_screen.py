# loading_screen.py
"""Loading screen with spinner animation and progress bar."""

import pygame
from utils import draw_progress_bar


class LoadingScreen:
    """Handles the loading screen with transition effects."""

    def __init__(self, design_width, design_height, current_width=None, current_height=None):
        """Initializes the loading screen with specific dimensions."""
        self.design_width = design_width
        self.design_height = design_height
        self.current_width = current_width or design_width
        self.current_height = current_height or design_height
        self.progress = 0
        self.alpha = 0
        self.fade_speed = 8
        self.active = True

        self.overlay = pygame.Surface((self.current_width, self.current_height), pygame.SRCALPHA)
        self.font = pygame.font.Font("src/assets/fonts/SpecialElite-Regular.ttf", 24)
        self.loading_text = self.font.render("Loading...", True, (255, 255, 255))
        self.spinner_angle = 0


    def update_screen_size(self, new_width, new_height):
        """Updates the screen dimensions when the window is resized or toggled to fullscreen."""
        self.current_width = new_width
        self.current_height = new_height
        self.overlay = pygame.Surface((new_width, new_height), pygame.SRCALPHA)


    def update_progress(self, progress):
        """Updates the loading progress."""
        self.progress = progress


    def start_fade_out(self):
        """Starts the fade-out effect to exit the loading screen."""
        self.active = False


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
        # Center the spinner in the current screen dimensions
        spinner_pos = (self.current_width//2 - rotated.get_width()//2, 
                       self.current_height//2 + 30)
        screen.blit(rotated, spinner_pos)


    def draw(self, screen):
        """Draws the loading screen."""
        # Create overlay with current dimensions
        self.overlay.fill((0, 0, 0, self.alpha))
        screen.blit(self.overlay, (0, 0))
        
        # Only show content if alpha is high enough (visibility)
        if self.alpha > 200:  
            # Use actual screen dimensions for drawing
            text_rect = self.loading_text.get_rect(center=(self.current_width//2, self.current_height//2 - 50))
            screen.blit(self.loading_text, text_rect)
            
            # Center the progress bar in the current screen
            progress_bar_width = 200
            progress_bar_height = 20
            progress_bar_x = self.current_width//2 - progress_bar_width//2
            progress_bar_y = self.current_height//2
            
            draw_progress_bar(screen, self.progress, 
                             (progress_bar_x, progress_bar_y, 
                              progress_bar_width, progress_bar_height))
            self.draw_spinner(screen)

        # Return True when the transition has ended
        is_finished = self.alpha == 0 and not self.active
        return is_finished