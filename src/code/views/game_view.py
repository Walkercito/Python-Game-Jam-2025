"""Main game view with player controls."""

import pygame
from utils import draw_fps
from src.code.player.player import Player
from constants import width, height, gray
from src.code.map.tile import TileMap
from src.code.camera import Camera


class GameView:
    """Handles the logic and rendering of the game view."""

    def __init__(self, switch_view, animation_paths, clock, font, show_fps=True):
        """Initializes the game view with necessary parameters."""
        self.switch_view = switch_view
        self.design_width = width
        self.design_height = height
        self.clock = clock
        self.font = font
        self.show_fps = show_fps
        
        self.player = Player(
            pos = (width // 2, height // 2),  
            animation_paths=animation_paths,
            speed = 140,
            scale = 0.5
        )
        self.current_scale = 1.0
        self.last_update_time = pygame.time.get_ticks()
        self.frame_time = 0

        # Load the map
        self.map = TileMap('./src/assets/map/floor.tmx')
        
        # Initialize the camera with a dead zone of 10% of the screen size
        self.camera = Camera(width, height, dead_zone_percent=0.1)
        # Center the camera on the player at the start
        self.camera.reset((self.player.rect.centerx, self.player.rect.centery))

    def handle_events(self, events):
        """Handles input events."""
        filtered_events = []
        for event in events:
            if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                filtered_events.append(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.switch_view("ingame_settings")

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
        """Updates the game logic with frame-independent timing."""
        dt = max(dt, 0.016)
        self.player.update(dt)
        
        # Update the camera to follow the player
        self.camera.update(self.player.rect, dt)

    def draw(self, screen):
        """Draws game elements."""
        screen.fill(gray)
        
        # Draw the map with camera offset
        self.map.draw_with_camera(screen, self.camera)
        
        # Draw the player with camera applied
        player_rect = self.camera.apply(self.player)
        screen.blit(self.player.image, player_rect)
        
        # Draw FPS
        draw_fps(screen, self.clock, self.font, screen.get_width(), self.show_fps)

    def handle_resize(self, new_width, new_height):
        """Adjusts the view when the window is resized."""
        scale_x = new_width / self.design_width
        scale_y = new_height / self.design_height
        
        self.current_scale = min(scale_x, scale_y)
        
        self.player.rect.center = (new_width // 2, new_height // 2)
        
        self.camera.width = new_width
        self.camera.height = new_height
        self.camera.dead_zone_x = new_width * self.camera.dead_zone_percent
        self.camera.dead_zone_y = new_height * self.camera.dead_zone_percent
        self.camera.dead_zone_rect = pygame.Rect(
            new_width // 2 - self.camera.dead_zone_x // 2, 
            new_height // 2 - self.camera.dead_zone_y // 2,
            self.camera.dead_zone_x, 
            self.camera.dead_zone_y
        )
        
        self.camera.reset((self.player.rect.centerx, self.player.rect.centery))