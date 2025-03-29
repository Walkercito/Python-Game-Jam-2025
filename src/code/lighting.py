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
        
        noise_x = random.uniform(-0.5, 0.5)
        noise_y = random.uniform(-0.5, 0.5)
        
        self.light_position = (
            base_x + wobble_x + noise_x,
            base_y + wobble_y + noise_y
        )
    
    def generate_baked_light_textures(self, num_steps=20):
        """Genera un conjunto de texturas de luz pre-renderizadas para diferentes niveles de influencia y energía.
        
        Args:
            num_steps: Número de pasos para discretizar los niveles de influencia y energía
        
        Returns:
            Un diccionario con las texturas pre-renderizadas
        """
        import constants as const
        import math
        
        # Limpiar el diccionario de texturas existentes
        const.baked_light_textures = {}
        
        # Generar texturas para diferentes niveles de influencia (antes del umbral crítico)
        for i in range(num_steps + 1):
            influence = i * (87.0 / num_steps)  # 0% a 87% en pasos discretos
            influence_key = math.floor(influence)
            
            # Calcular el radio de luz para este nivel de influencia
            base_max_radius = min(self.screen_width, self.screen_height) * 0.35
            min_radius = base_max_radius * 0.5
            influence_factor = influence / 87.0
            adjusted_factor = influence_factor ** 0.7
            radius = min_radius + (base_max_radius - min_radius) * adjusted_factor
            
            # Generar y guardar la textura
            texture = self.create_light_texture(radius, self.light_intensity)
            const.baked_light_textures[f"pre_threshold_{influence_key}"] = texture
        
        # Generar texturas para diferentes niveles de energía (después del umbral crítico)
        # Usar el radio máximo alcanzado en el umbral crítico
        max_radius = min_radius + (base_max_radius - min_radius) * ((87.0 / 87.0) ** 0.7)
        
        for i in range(num_steps + 1):
            energy = i * (100.0 / num_steps)  # 0% a 100% en pasos discretos
            energy_key = math.floor(energy)
            
            # Calcular el radio de luz para este nivel de energía
            energy_factor = energy / 100.0
            radius = max(10, max_radius * energy_factor)
            intensity = max(50, 255 * energy_factor)
            
            # Generar y guardar la textura
            texture = self.create_light_texture(radius, intensity)
            const.baked_light_textures[f"post_threshold_{energy_key}"] = texture
        
        print(f"Generadas {len(const.baked_light_textures)} texturas de luz pre-renderizadas")
        return const.baked_light_textures
    
    def create_light_texture(self, radius, intensity):
        """Crea una textura de luz con el radio e intensidad especificados.
        
        Args:
            radius: Radio de la luz
            intensity: Intensidad de la luz (0-255)
            
        Returns:
            La textura de luz generada
        """
        texture_size = int(radius * 3.0)
        texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        
        center = texture_size // 2
        
        for y in range(texture_size):
            for x in range(texture_size):
                dx, dy = x - center, y - center
                distance = math.sqrt(dx*dx + dy*dy) / radius
                
                if distance < 1.2:
                    falloff = max(0, 1.0 - distance*distance*distance*0.7)
                    falloff = falloff ** 0.7
                    
                    alpha = int(intensity * falloff)
                    texture.set_at((x, y), (255, 255, 255, alpha))
        
        return texture
    
    def get_baked_light_texture(self, influence, energy, threshold_reached):
        """Obtiene la textura de luz pre-renderizada más cercana a los valores actuales.
        
        Args:
            influence: Porcentaje de influencia actual (0-100)
            energy: Porcentaje de energía actual (0-100)
            threshold_reached: Si se ha alcanzado el umbral crítico
            
        Returns:
            La textura de luz pre-renderizada más adecuada
        """
        import constants as const
        import math
        
        if not const.baked_light_textures:
            return None
        
        if threshold_reached:
            # Después del umbral, usar la textura basada en energía
            energy_key = math.floor(energy)
            # Buscar la textura más cercana
            while energy_key >= 0:
                key = f"post_threshold_{energy_key}"
                if key in const.baked_light_textures:
                    return const.baked_light_textures[key]
                energy_key -= 1
        else:
            # Antes del umbral, usar la textura basada en influencia
            influence_key = math.floor(influence)
            # Buscar la textura más cercana
            while influence_key >= 0:
                key = f"pre_threshold_{influence_key}"
                if key in const.baked_light_textures:
                    return const.baked_light_textures[key]
                influence_key -= 1
        
        # Si no se encuentra ninguna textura adecuada, devolver None
        return None
    
    def set_baked_lights_mode(self, enabled):
        """Activa o desactiva el modo de luces pre-renderizadas.
        
        Args:
            enabled: True para activar, False para desactivar
        """
        self.using_baked_lights = enabled
        
    def draw(self, surface, influence=None, energy=None, threshold_reached=False):
        """Draws the lighting effect on the given surface.
        
        Args:
            surface: Superficie donde dibujar la luz
            influence: Porcentaje de influencia actual (0-100)
            energy: Porcentaje de energía actual (0-100)
            threshold_reached: Si se ha alcanzado el umbral crítico
        """
        import constants as const
        
        self.light_surface.fill((0, 0, 0, 255 - self.ambient_light))
        
        # Si estamos usando luces pre-renderizadas y tenemos los valores de influencia y energía
        if self.using_baked_lights and const.use_baked_lights and influence is not None and energy is not None:
            # Obtener la textura pre-renderizada adecuada
            baked_texture = self.get_baked_light_texture(influence, energy, threshold_reached)
            
            if baked_texture is not None:
                # Usar la textura pre-renderizada
                pos_x = int(self.light_position[0] - baked_texture.get_width() // 2)
                pos_y = int(self.light_position[1] - baked_texture.get_height() // 2)
                self.light_surface.blit(baked_texture, (pos_x, pos_y), special_flags=pygame.BLEND_RGBA_SUB)
            else:
                # Si no hay textura pre-renderizada, usar la generada dinámicamente
                pos_x = int(self.light_position[0] - self.light_texture.get_width() // 2)
                pos_y = int(self.light_position[1] - self.light_texture.get_height() // 2)
                self.light_surface.blit(self.light_texture, (pos_x, pos_y), special_flags=pygame.BLEND_RGBA_SUB)
        else:
            # Usar la textura generada dinámicamente
            pos_x = int(self.light_position[0] - self.light_texture.get_width() // 2)
            pos_y = int(self.light_position[1] - self.light_texture.get_height() // 2)
            self.light_surface.blit(self.light_texture, (pos_x, pos_y), special_flags=pygame.BLEND_RGBA_SUB)
        
        surface.blit(self.light_surface, (0, 0))
