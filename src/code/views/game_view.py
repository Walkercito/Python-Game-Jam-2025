"""Main game view with player controls."""

import pygame
from utils import draw_fps
from src.code.player.player import Player
from src.code.npc.npc import NPCManager
from constants import width, height, gray
from src.code.map.tile import TileMap
from src.code.camera import Camera


class GameView:
    """Handles the logic and rendering of the game view."""

    def __init__(self, switch_view, animation_paths, npc_animation_paths,clock, font, show_fps=True):
        """Initializes the game view with necessary parameters."""
        self.switch_view = switch_view
        self.design_width = width
        self.design_height = height
        self.clock = clock
        self.font = font
        self.show_fps = show_fps
        
        current_screen = pygame.display.get_surface()
        current_width, current_height = current_screen.get_size()
        
        self.player = Player(
            pos = (current_width // 2, current_height // 2), 
            animation_paths = animation_paths,
            speed = 140,
            scale = 0.5
        )
        self.current_scale = 1.0
        self.last_update_time = pygame.time.get_ticks()
        self.frame_time = 0

        # Load the map
        self.map = TileMap('./src/assets/map/floor.tmx')
        
        # Initialize the camera with a dead zone of 10% of the screen size
        self.camera = Camera(current_width, current_height, dead_zone_percent = 0.1)
        self.camera.reset((self.player.rect.centerx, self.player.rect.centery))
        
        self.npc_manager = NPCManager(npc_animation_paths, current_width, current_height)

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
        
        # Handle NPC interaction with E key
        self.npc_manager.handle_interaction(self.player.rect, keys)

    def update(self, dt):
        """Updates the game logic with frame-independent timing."""
        dt = max(dt, 0.016)
        self.player.update(dt)
        
        # Update NPCs - passing the camera reference
        self.npc_manager.update(dt, self.player.rect, self.camera)
        self.camera.update(self.player.rect, dt)

    def draw(self, screen):
        """Draws game elements."""
        screen.fill(gray)

        self.map.draw_with_camera(screen, self.camera)
        
        # Draw NPCs with camera offset
        self.npc_manager.draw(screen, self.camera)
        
        # Draw the player with camera applied
        player_rect = self.camera.apply(self.player)
        screen.blit(self.player.image, player_rect)

        draw_fps(screen, self.clock, self.font, screen.get_width(), self.show_fps)

    def handle_resize(self, new_width, new_height):
        """Adjusts the view when the window is resized."""
        scale_x = new_width / self.design_width
        scale_y = new_height / self.design_height
        
        self.current_scale = min(scale_x, scale_y)
        
        self.camera.width = new_width
        self.camera.height = new_height
        
        # Update camera dead zone
        self.camera.dead_zone_percent = 0.1  # Fixed value for consistency
        self.camera.dead_zone_x = new_width * self.camera.dead_zone_percent
        self.camera.dead_zone_y = new_height * self.camera.dead_zone_percent
        self.camera.dead_zone_rect = pygame.Rect(
            new_width // 2 - self.camera.dead_zone_x // 2, 
            new_height // 2 - self.camera.dead_zone_y // 2,
            self.camera.dead_zone_x, 
            self.camera.dead_zone_y
        )
        
        self.camera.force_center = True

        self.npc_manager.screen_width = new_width
        self.npc_manager.screen_height = new_height
        self.npc_manager.update_spawn_zones()

    def handle_fullscreen_change(self, screen_width, screen_height, is_fullscreen):
        """Handles the transition between windowed and fullscreen modes."""
        self.player.rect.center = (screen_width // 2, screen_height // 2)
        
        if hasattr(self.player, '_float_pos'):
            self.player._float_pos.x = self.player.rect.x
            self.player._float_pos.y = self.player.rect.y

        self.player.direction = pygame.math.Vector2(0, 0)

        self.camera.width = screen_width
        self.camera.height = screen_height
        
        if is_fullscreen:
            self.camera.set_zoom(3.0)
        else:
            self.camera.set_zoom(1.0)
        
        # Update camera dead zone
        self.camera.dead_zone_x = self.camera.width * self.camera.dead_zone_percent
        self.camera.dead_zone_y = self.camera.height * self.camera.dead_zone_percent
        self.camera.dead_zone_rect = pygame.Rect(
            self.camera.width // 2 - self.camera.dead_zone_x // 2, 
            self.camera.height // 2 - self.camera.dead_zone_y // 2,
            self.camera.dead_zone_x, 
            self.camera.dead_zone_y
        )
        
        # Center camera
        self.camera.reset((self.player.rect.centerx, self.player.rect.centery))
            
        # Update NPCs
        self.npc_manager.screen_width = screen_width
        self.npc_manager.screen_height = screen_height
        self.npc_manager.update_spawn_zones()