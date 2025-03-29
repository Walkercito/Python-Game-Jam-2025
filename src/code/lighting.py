"""Lighting system using pure Pygame for dynamic lighting effects - OPTIMIZED VERSION."""

import pygame
import math
import random
import numpy as np

class LightingSystem:
    """Handles the lighting effects in the game."""
    
    def __init__(self, screen_width, screen_height):
        """Initializes the lighting system."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.light_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        self.light_radius = min(screen_width, screen_height) * 0.35
        self.ambient_light = 10  # 0-255, 0 is completely dark
        self.light_intensity = 255 
        
        self.wobble_amount = 2.0
        self.wobble_speed = 0.05
        self.wobble_time = 0
        
        self.light_position = (screen_width // 2, screen_height // 2)
        
        # Variables for bake
        self.using_baked_lights = False
        self.current_baked_light = None
        self.last_influence_value = 0
        self.last_energy_value = 100
        
        # Cache for textures
        self.texture_cache = {}
        
        # Generate base light texture once
        self.generate_light_texture()
        
    def generate_light_texture(self):
        """Generates a smooth circular light texture."""
        texture_size = int(self.light_radius * 3.0)
        self.light_texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        
        # Use numpy for faster pixel operations
        center = texture_size // 2
        arr = np.zeros((texture_size, texture_size, 4), dtype=np.uint8)
        
        # Generate coordinates grid
        y, x = np.ogrid[:texture_size, :texture_size]
        dx, dy = x - center, y - center
        distance = np.sqrt(dx*dx + dy*dy) / self.light_radius
        
        # Calculate falloff
        mask = distance < 1.2
        falloff = np.zeros_like(distance)
        falloff[mask] = np.maximum(0, 1.0 - distance[mask]**3 * 0.7) ** 0.7
        
        # Set RGBA values
        arr[..., 0] = 255  # R
        arr[..., 1] = 255  # G
        arr[..., 2] = 255  # B
        arr[..., 3] = (self.light_intensity * falloff).astype(np.uint8)  # A
        
        # Create pygame surface from numpy array
        pygame_surface = pygame.surfarray.make_surface(arr[:, :, :3])
        pygame_surface.set_alpha(255)
        
        # Create alpha channel
        alpha_surface = pygame.surfarray.make_surface(arr[:, :, 3])
        pygame_surface.set_colorkey((0, 0, 0))
        
        # Combine surfaces
        self.light_texture.blit(pygame_surface, (0, 0))
        self.light_texture.set_alpha(255)
    
    def resize(self, new_width, new_height):
        """Resizes the lighting system for a new screen size."""
        self.screen_width = new_width
        self.screen_height = new_height
        self.light_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
        
        old_radius = self.light_radius
        self.light_radius = min(new_width, new_height) * 0.35 
        if abs(self.light_radius - old_radius) > 5:
            self.generate_light_texture()
    
    def update(self, player_center, camera, dt=1/60):
        """Updates the light position based on player position."""
        screen_pos = camera.apply_point((player_center[0], player_center[1]))
        base_x, base_y = int(screen_pos[0]), int(screen_pos[1])
        
        self.wobble_time += dt * self.wobble_speed
        
        wobble_x = math.sin(self.wobble_time * 5.2) * self.wobble_amount
        wobble_y = math.cos(self.wobble_time * 4.7) * self.wobble_amount
        
        # Optional: reduce random noise calculation frequency
        if random.random() < 0.3:  # Only calculate new noise 30% of the time
            self.noise_x = random.uniform(-0.5, 0.5)
            self.noise_y = random.uniform(-0.5, 0.5)
        
        self.light_position = (
            base_x + wobble_x + getattr(self, 'noise_x', 0),
            base_y + wobble_y + getattr(self, 'noise_y', 0)
        )
    
    def generate_baked_light_textures(self, num_steps=10):
        """Generates a set of pre-rendered light textures for different levels.
        Reduced number of steps for better performance.
        """
        import constants as const
        import math

        const.baked_light_textures = {}
        
        base_max_radius = min(self.screen_width, self.screen_height) * 0.35
        min_radius = base_max_radius * 0.5
        
        # Generate fewer textures with larger steps
        for i in range(num_steps + 1):
            influence = i * (87.0 / num_steps) 
            influence_key = math.floor(influence)
            
            influence_factor = influence / 87.0
            adjusted_factor = influence_factor ** 0.7
            radius = min_radius + (base_max_radius - min_radius) * adjusted_factor
            
            # Use cached texture if already generated
            cache_key = f"radius_{int(radius)}_intensity_{self.light_intensity}"
            if cache_key in self.texture_cache:
                texture = self.texture_cache[cache_key]
            else:
                texture = self.create_light_texture(radius, self.light_intensity)
                self.texture_cache[cache_key] = texture
                
            const.baked_light_textures[f"pre_threshold_{influence_key}"] = texture

        max_radius = min_radius + (base_max_radius - min_radius) * ((87.0 / 87.0) ** 0.7)
        
        for i in range(num_steps + 1):
            energy = i * (100.0 / num_steps) 
            energy_key = math.floor(energy)

            energy_factor = energy / 100.0
            radius = max(10, max_radius * energy_factor)
            intensity = max(50, 255 * energy_factor)
            
            # Use cached texture if already generated
            cache_key = f"radius_{int(radius)}_intensity_{int(intensity)}"
            if cache_key in self.texture_cache:
                texture = self.texture_cache[cache_key]
            else:
                texture = self.create_light_texture(radius, intensity)
                self.texture_cache[cache_key] = texture
                
            const.baked_light_textures[f"post_threshold_{energy_key}"] = texture
        
        print(f"Generadas {len(const.baked_light_textures)} texturas de luz pre-renderizadas")
        return const.baked_light_textures
    
    def create_light_texture(self, radius, intensity):
        """Creates a light texture with the specified radius and intensity using numpy for speed."""
        texture_size = int(radius * 3.0)
        texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        
        # Use numpy for faster pixel operations
        center = texture_size // 2
        
        # Create coordinate grid once
        y, x = np.ogrid[:texture_size, :texture_size]
        dx, dy = x - center, y - center
        distance = np.sqrt(dx*dx + dy*dy) / radius
        
        # Create falloff mask
        mask = distance < 1.2
        
        # Create surface from numpy array
        surface_array = np.zeros((texture_size, texture_size, 4), dtype=np.uint8)
        surface_array[..., :3] = 255  # RGB channels
        
        # Calculate alpha only where needed
        falloff = np.zeros_like(distance)
        falloff[mask] = np.maximum(0, 1.0 - distance[mask]**3 * 0.7) ** 0.7
        surface_array[..., 3] = (intensity * falloff).astype(np.uint8)
        
        # Convert to pygame surface - faster method
        pygame.surfarray.pixels_alpha(texture)[:] = surface_array[..., 3]
        pygame.surfarray.pixels_red(texture)[:] = surface_array[..., 0]
        pygame.surfarray.pixels_green(texture)[:] = surface_array[..., 1]
        pygame.surfarray.pixels_blue(texture)[:] = surface_array[..., 2]
        
        return texture
    
    def get_baked_light_texture(self, influence, energy, threshold_reached):
        """Gets the pre-rendered light texture closest to the current values.
        Optimized to reduce texture switching.
        """
        import constants as const
        import math
        
        if not const.baked_light_textures:
            return None
            
        # Round to nearest 10 to reduce texture switching
        if threshold_reached:
            energy_key = math.floor(energy / 10) * 10
            key = f"post_threshold_{energy_key}"
            if key in const.baked_light_textures:
                return const.baked_light_textures[key]
            
            # Fallback to closest lower value
            while energy_key >= 0:
                energy_key -= 10
                key = f"post_threshold_{energy_key}"
                if key in const.baked_light_textures:
                    return const.baked_light_textures[key]
        else:
            influence_key = math.floor(influence / 10) * 10
            key = f"pre_threshold_{influence_key}"
            if key in const.baked_light_textures:
                return const.baked_light_textures[key]
                
            # Fallback to closest lower value
            while influence_key >= 0:
                influence_key -= 10
                key = f"pre_threshold_{influence_key}"
                if key in const.baked_light_textures:
                    return const.baked_light_textures[key]
        
        return None
    
    def set_baked_lights_mode(self, enabled):
        """Enables or disables the baked lights mode."""
        self.using_baked_lights = enabled
        
    def draw(self, surface, influence=None, energy=None, threshold_reached=False):
        """Draws the lighting effect on the given surface.
        Optimized version that reuses surfaces when possible.
        """
        import constants as const
        
        # Only clear the surface when needed
        self.light_surface.fill((0, 0, 0, 255 - self.ambient_light))
        
        # Cache influence and energy values to reduce texture switching
        if influence is not None:
            influence = round(influence / 5) * 5  # Round to nearest 5
        if energy is not None:
            energy = round(energy / 5) * 5  # Round to nearest 5
            
        # Check if we need to switch textures
        needs_texture_update = (
            (self.last_influence_value != influence and influence is not None) or
            (self.last_energy_value != energy and energy is not None)
        )
        
        # Get or keep the current texture
        current_texture = None
        if self.using_baked_lights and const.use_baked_lights and influence is not None and energy is not None:
            if needs_texture_update or self.current_baked_light is None:
                self.current_baked_light = self.get_baked_light_texture(influence, energy, threshold_reached)
                self.last_influence_value = influence
                self.last_energy_value = energy
            
            current_texture = self.current_baked_light or self.light_texture
        else:
            current_texture = self.light_texture
            
        # Draw the light
        if current_texture:
            pos_x = int(self.light_position[0] - current_texture.get_width() // 2)
            pos_y = int(self.light_position[1] - current_texture.get_height() // 2)
            self.light_surface.blit(current_texture, (pos_x, pos_y), special_flags=pygame.BLEND_RGBA_SUB)
        
        # Final blit to screen
        surface.blit(self.light_surface, (0, 0))