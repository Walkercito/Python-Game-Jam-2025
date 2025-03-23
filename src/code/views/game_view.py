"""Main game view with player controls."""

import pygame
from utils import draw_fps
from src.code.player.player import Player
from constants import width, height, gray


class GameView:
    """Handles the logic and rendering of the game view."""

    def __init__(self, switch_view, animation_paths, clock, font):
        """Initializes the game view with necessary parameters."""
        self.switch_view = switch_view
        self.design_width = width
        self.design_height = height
        self.clock = clock
        self.font = font
        
        self.player = Player(
            pos = (width // 2, height // 2),  
            animation_paths=animation_paths,
            speed = 200,
            scale = 0.5
        )
        self.current_scale = 1.0

    def handle_events(self, events):
        """Handles input events."""
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch_view("main")

        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]: direction.y = -1
        if keys[pygame.K_s]: direction.y = 1
        if keys[pygame.K_a]: direction.x = -1
        if keys[pygame.K_d]: direction.x = 1
        
        if direction.length() > 0:
            direction.normalize_ip()
        
        self.player.move(direction)

    def update(self, dt):
        """Updates the game logic."""
        self.player.update(dt)

    def draw(self, screen):
        """Draws the game elements."""
        screen.fill(gray)
        draw_fps(screen, self.clock, self.font, screen.get_width())
        screen.blit(self.player.image, self.player.rect)

    def handle_resize(self, new_width, new_height):
        """Adjusts the view when the window is resized."""
        scale_x = new_width / self.design_width
        scale_y = new_height / self.design_height
        self.player.rect.center = (new_width // 2, new_height // 2)
        self.player.speed = 200 * scale_x
