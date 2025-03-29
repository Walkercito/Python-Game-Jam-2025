"""Intro screen that shows at game startup."""

import pygame
import asyncio


class IntroScreen:
    """Handles the intro sequence with fading transitions."""

    def __init__(self, design_width, design_height, current_width=None, current_height=None):
        """Initializes the intro screen with specific dimensions."""
        self.design_width = design_width
        self.design_height = design_height
        self.current_width = current_width or design_width
        self.current_height = current_height or design_height
        
        self.alpha = 0
        self.fade_speed = 5
        self.active = True
        self.completed = False
        
        # Sequence state
        self.current_sequence = 0  # 0: pygame-ce, 1: Qva Team, 2: finished
        self.sequence_pause = 1.0  # Pause between sequences in seconds
        self.sequence_timer = 0
        self.fading_out = False
        
        # Create overlay surface
        self.overlay = pygame.Surface((self.current_width, self.current_height))
        self.overlay.fill((0, 0, 0))
        
        # Load fonts
        self.font_large = pygame.font.Font("src/assets/fonts/SpecialElite-Regular.ttf", 36)
        self.font_medium = pygame.font.Font("src/assets/fonts/SpecialElite-Regular.ttf", 28)
        
        # Prepare text
        self.pygame_text = self.font_large.render("Made with pygame-ce", True, (255, 255, 255))
        self.team_text = self.font_large.render("QvaX Team", True, (255, 255, 255))
        
        # Centering rectangles
        self.pygame_rect = self.pygame_text.get_rect(center=(self.current_width//2, self.current_height//2))
        self.team_rect = self.team_text.get_rect(center=(self.current_width//2, self.current_height//2))
        
        # Loading text for background tasks
        self.loading_text = self.font_medium.render("Loading...", True, (150, 150, 150))
        self.loading_rect = self.loading_text.get_rect(bottomright=(self.current_width - 20, self.current_height - 20))
    
    def update_screen_size(self, new_width, new_height):
        """Updates the screen dimensions when the window is resized."""
        self.current_width = new_width
        self.current_height = new_height
        self.overlay = pygame.Surface((new_width, new_height))
        self.overlay.fill((0, 0, 0))
        
        # Update text positions
        self.pygame_rect = self.pygame_text.get_rect(center=(new_width//2, new_height//2))
        self.team_rect = self.team_text.get_rect(center=(new_width//2, new_height//2))
        self.loading_rect = self.loading_text.get_rect(bottomright=(new_width - 20, new_height - 20))
    
    def update(self, dt):
        """Updates the intro screen state and animations."""
        if not self.active:
            return True
            
        # Handle fade in/out
        if not self.fading_out and self.alpha < 255:
            self.alpha = min(self.alpha + self.fade_speed, 255)
        elif self.fading_out and self.alpha > 0:
            self.alpha = max(self.alpha - self.fade_speed, 0)
            
            # Move to next sequence when fade out is complete
            if self.alpha == 0:
                if self.current_sequence < 2:
                    self.current_sequence += 1
                    self.fading_out = False
                else:
                    self.completed = True
                    self.active = False
        
        # Handle pause between fade in and fade out
        if self.alpha == 255 and not self.fading_out:
            self.sequence_timer += dt
            if self.sequence_timer >= self.sequence_pause:
                self.fading_out = True
                self.sequence_timer = 0
                
        return self.completed
                
    def draw(self, screen):
        """Draws the intro screen with the current sequence."""
        if not self.active:
            return
            
        # Fill screen with black
        screen.fill((0, 0, 0))
        
        # Draw current sequence text with alpha
        if self.current_sequence == 0:
            # pygame-ce text
            self.pygame_text.set_alpha(self.alpha)
            screen.blit(self.pygame_text, self.pygame_rect)
        elif self.current_sequence == 1:
            # Qva Team text
            self.team_text.set_alpha(self.alpha)
            screen.blit(self.team_text, self.team_rect)
            
        # Always show loading indicator with reduced alpha
        loading_alpha = min(self.alpha, 180)
        self.loading_text.set_alpha(loading_alpha)
        screen.blit(self.loading_text, self.loading_rect)
        
        return self.completed
