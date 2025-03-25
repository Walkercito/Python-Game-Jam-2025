"""Lighting system using pure Pygame for dynamic lighting effects."""

import pygame
import math
import random

class LightingSystem:
    """Handles the lighting effects in the game."""
    
    def __init__(self, screen_width, screen_height):
        """Initializes the lighting system."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.light_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        self.light_radius = min(screen_width, screen_height) * 0.25
        self.ambient_light = 10  # 0-255, 0 is completely dark
        self.light_intensity = 255  # Maximum light intensity
        
        self.wobble_amount = 2.0
        self.wobble_speed = 0.05
        self.wobble_time = 0
        
        self.light_position = (screen_width // 2, screen_height // 2)
        
        self.generate_light_texture()
        
    def generate_light_texture(self):
        """Generates a smooth circular light texture."""
        texture_size = int(self.light_radius * 3.0)
        self.light_texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        
        center = texture_size // 2
        
        for y in range(texture_size):
            for x in range(texture_size):
                dx, dy = x - center, y - center
                distance = math.sqrt(dx*dx + dy*dy) / self.light_radius
                
                if distance < 1.2:
                    falloff = max(0, 1.0 - distance*distance*distance*0.7)
                    falloff = falloff ** 0.7
                    
                    alpha = int(self.light_intensity * falloff)
                    self.light_texture.set_at((x, y), (255, 255, 255, alpha))
    
    def resize(self, new_width, new_height):
        """Resizes the lighting system for a new screen size."""
        self.screen_width = new_width
        self.screen_height = new_height
        self.light_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
        
        old_radius = self.light_radius
        self.light_radius = min(new_width, new_height) * 0.25
        
        if abs(self.light_radius - old_radius) > 5:
            self.generate_light_texture()
    
    def update(self, player_center, camera, dt=1/60):
        """Updates the light position based on player position."""
        screen_pos = camera.apply_point((player_center[0], player_center[1]))
        base_x, base_y = int(screen_pos[0]), int(screen_pos[1])
        
        self.wobble_time += dt * self.wobble_speed
        
        wobble_x = math.sin(self.wobble_time * 5.2) * self.wobble_amount
        wobble_y = math.cos(self.wobble_time * 4.7) * self.wobble_amount
        
        noise_x = random.uniform(-0.5, 0.5)
        noise_y = random.uniform(-0.5, 0.5)
        
        self.light_position = (
            base_x + wobble_x + noise_x,
            base_y + wobble_y + noise_y
        )
    
    def draw(self, surface):
        """Draws the lighting effect on the given surface."""
        self.light_surface.fill((0, 0, 0, 255 - self.ambient_light))
        
        pos_x = int(self.light_position[0] - self.light_texture.get_width() // 2)
        pos_y = int(self.light_position[1] - self.light_texture.get_height() // 2)
        
        self.light_surface.blit(self.light_texture, (pos_x, pos_y), special_flags=pygame.BLEND_RGBA_SUB)
        
        surface.blit(self.light_surface, (0, 0))
