"""Lighting system using pure Pygame for dynamic lighting effects."""

import pygame
import math
import random
import constants as const

class LightingSystem:
    """Handles the lighting effects in the game."""
    
    def __init__(self, screen_width, screen_height):
        """Initializes the lighting system."""
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        self.light_surface = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        
        self.light_radius = min(screen_width, screen_height) * 0.25
        self.base_light_radius = self.light_radius
        self.max_light_radius = min(screen_width, screen_height) * 0.6  # Aumentado de 0.4 a 0.6 para un efecto más notable
        self.min_light_radius = min(screen_width, screen_height) * 0.1  # Disminuido de 0.15 a 0.1 para un efecto más oscuro
        
        self.ambient_light = 10  # 0-255, 0 is completely dark
        self.base_ambient_light = self.ambient_light
        self.max_ambient_light = 60  # Aumentado de 40 a 60 para más brillo
        self.min_ambient_light = 3   # Disminuido de 5 a 3 para más oscuridad
        
        self.light_intensity = 255  # Maximum light intensity
        self.base_light_intensity = self.light_intensity
        self.max_light_intensity = 255  # Maximum intensity with high conviction
        self.min_light_intensity = 160  # Disminuido de 180 a 160 para más contraste
        
        self.wobble_amount = 2.0
        self.wobble_speed = 0.05
        self.wobble_time = 0
        
        self.light_position = (screen_width // 2, screen_height // 2)
        
        # Target values for smooth transitions
        self.target_light_radius = self.light_radius
        self.target_ambient_light = self.ambient_light
        self.target_light_intensity = self.light_intensity
        
        # Transition speed (lower = smoother/slower)
        self.transition_speed = 1.0
        
        # Pre-renderizar texturas de luz para diferentes tamaños
        self.light_textures = {}
        self.prerender_light_textures()
        
    def prerender_light_textures(self):
        """Pre-renders light textures of different sizes for better performance."""
        # Volvemos a usar 8 texturas como originalmente
        num_textures = 8
        min_radius = self.min_light_radius * 0.9  # Ligeramente más pequeño que el mínimo
        max_radius = self.max_light_radius * 1.1  # Ligeramente más grande que el máximo
        
        step = (max_radius - min_radius) / (num_textures - 1)
        
        for i in range(num_textures):
            radius = min_radius + step * i
            # Guardamos la textura con el radio como clave (redondeado a entero)
            key = int(radius)
            self.light_textures[key] = self.create_light_texture(radius, self.light_intensity)
            
    def create_light_texture(self, radius, intensity):
        """Creates a light texture with the given radius and intensity."""
        texture_size = int(radius * 3.0)
        if texture_size < 10:  # Aseguramos un tamaño mínimo para evitar errores
            texture_size = 10
            
        texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        
        center = texture_size // 2
        
        for y in range(texture_size):
            for x in range(texture_size):
                dx, dy = x - center, y - center
                distance = math.sqrt(dx*dx + dy*dy) / radius
                
                if distance < 1.2:
                    falloff = max(0, 1.0 - distance*distance*distance*0.7)
                    falloff = falloff ** 0.7
                    
                    # Aseguramos que alpha esté dentro del rango [0, 255]
                    alpha = max(0, min(255, int(intensity * falloff)))
                    texture.set_at((x, y), (255, 255, 255, alpha))
                    
        return texture
        
    def generate_light_texture(self):
        """Generates a smooth circular light texture."""
        texture_size = int(self.light_radius * 3.0)
        # Aseguramos un tamaño mínimo para la textura
        if texture_size < 10:
            texture_size = 10
            
        self.light_texture = pygame.Surface((texture_size, texture_size), pygame.SRCALPHA)
        
        center = texture_size // 2
        
        for y in range(texture_size):
            for x in range(texture_size):
                dx, dy = x - center, y - center
                distance = math.sqrt(dx*dx + dy*dy) / self.light_radius
                
                if distance < 1.2:
                    falloff = max(0, 1.0 - distance*distance*distance*0.7)
                    falloff = falloff ** 0.7
                    
                    # Aseguramos que alpha esté dentro del rango [0, 255]
                    alpha = max(0, min(255, int(self.light_intensity * falloff)))
                    self.light_texture.set_at((x, y), (255, 255, 255, alpha))
    
    def resize(self, new_width, new_height):
        """Resizes the lighting system for a new screen size."""
        self.screen_width = new_width
        self.screen_height = new_height
        self.light_surface = pygame.Surface((new_width, new_height), pygame.SRCALPHA)
        
        old_radius = self.light_radius
        self.base_light_radius = min(new_width, new_height) * 0.25
        self.max_light_radius = min(new_width, new_height) * 0.6
        self.min_light_radius = min(new_width, new_height) * 0.1
        
        # Keep the current ratio of light_radius to base_light_radius
        ratio = self.light_radius / old_radius if old_radius > 0 else 1.0
        self.light_radius = self.base_light_radius * ratio
        self.target_light_radius = self.light_radius
        
        # Re-prerender las texturas con los nuevos tamaños
        self.light_textures = {}
        self.prerender_light_textures()
        
        if abs(self.light_radius - old_radius) > 5:
            self.generate_light_texture()
    
    def get_closest_light_texture(self, radius):
        """Returns the pre-rendered texture closest to the desired radius."""
        # Encontrar la clave más cercana
        closest_key = None
        min_diff = float('inf')
        
        for key in self.light_textures:
            diff = abs(key - radius)
            if diff < min_diff:
                min_diff = diff
                closest_key = key
        
        # Si no encontramos una textura cercana, generamos una nueva
        if closest_key is None:
            # Generamos la textura y la añadimos al diccionario
            key = int(radius)
            self.light_textures[key] = self.create_light_texture(radius, self.light_intensity)
            return self.light_textures[key]
            
        return self.light_textures[closest_key]
    
    def update(self, player_center, camera, dt=1/60, player=None):
        """Updates the light position based on player position and attributes."""
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
        
        # Update lighting based on player conviction and influence
        if player:
            conviction_rate = player.get_conviction_rate() if hasattr(player, 'get_conviction_rate') else 0.5
            influence = player.influence_percentage if hasattr(player, 'influence_percentage') else 0
            critical_threshold = player.critical_influence_threshold if hasattr(player, 'critical_influence_threshold') else 87.0
            energy = player.energy_percentage if hasattr(player, 'energy_percentage') else 100.0
            
            # Calcular el factor de luz basado en la convicción
            conviction_boost = (conviction_rate - 0.5) * 2.0  # Scale from -1.0 to 1.0
            conviction_factor = max(0.0, conviction_boost * 1.5)  # Amplificado para más efecto visual
            
            # El radio de luz, luz ambiental e intensidad son DIRECTAMENTE PROPORCIONALES a la influencia actual 
            # No reducimos automáticamente al superar el umbral crítico
            
            # Calcular tamaño de luz basado en influencia (directamente proporcional)
            # Al 0% de influencia -> tamaño mínimo
            # Al 100% de influencia -> tamaño máximo
            influence_factor = influence / 100.0  # Normalizado entre 0-1
            
            # Light radius aumenta con la influencia
            self.target_light_radius = self.min_light_radius + (self.max_light_radius - self.min_light_radius) * influence_factor
            
            # También aplicamos un boost según la convicción (efecto adicional)
            conviction_boost_amount = conviction_factor * (self.max_light_radius - self.base_light_radius) * 0.4  # 40% del efecto máximo
            self.target_light_radius += conviction_boost_amount
            
            # Ambient light aumenta con la influencia
            self.target_ambient_light = self.min_ambient_light + (self.max_ambient_light - self.min_ambient_light) * influence_factor
            
            # Light intensity aumenta con la influencia
            self.target_light_intensity = self.min_light_intensity + (self.max_light_intensity - self.min_light_intensity) * influence_factor
            
            # Ajustamos la velocidad de transición 
            transition_speed = self.transition_speed
            
            # Transición más suave para cambios graduales, especialmente para luces en tiempo real
            if not const.use_prerendered_lights:
                # Para luces en tiempo real, siempre usamos transiciones suaves
                transition_speed = self.transition_speed * 0.7
            
            # Smoothly transition current values toward target values
            self.light_radius += (self.target_light_radius - self.light_radius) * transition_speed * dt * 30
            self.ambient_light += (self.target_ambient_light - self.ambient_light) * transition_speed * dt * 30
            self.light_intensity += (self.target_light_intensity - self.light_intensity) * transition_speed * dt * 30
            
            # Limitamos los valores para evitar errores
            self.light_radius = max(1.0, self.light_radius)  # Evitar radios negativos o demasiado pequeños
            self.ambient_light = max(0, min(255, self.ambient_light))
            self.light_intensity = max(0, min(255, self.light_intensity))
            
    def draw(self, surface):
        """Draws the lighting effect on the given surface."""
        # Llenar la superficie de luz con un color negro semi-transparente
        self.light_surface.fill((0, 0, 0, 255 - self.ambient_light))
        
        if const.use_prerendered_lights:
            # Método prerrenderizado (usa texturas precalculadas)
            # Obtenemos la textura de luz más cercana al radio actual
            light_texture = self.get_closest_light_texture(self.light_radius)
            
            # Posicionamos la textura de luz centrada en la posición del jugador
            texture_size = light_texture.get_width()
            position = (int(self.light_position[0] - texture_size//2), 
                       int(self.light_position[1] - texture_size//2))
            
            # Dibujamos la textura de luz en modo "subtract" para crear el efecto de iluminación
            self.light_surface.blit(light_texture, position, special_flags=pygame.BLEND_RGBA_SUB)
        else:
            # Método de generación en tiempo real (original)
            # Calculamos el centro y la intensidad de la luz
            center_x, center_y = int(self.light_position[0]), int(self.light_position[1])
            intensity = int(self.light_intensity)
            radius = int(self.light_radius)
            
            # Dibujamos la luz circular
            for y in range(max(0, center_y - radius), min(self.screen_height, center_y + radius + 1)):
                for x in range(max(0, center_x - radius), min(self.screen_width, center_x + radius + 1)):
                    dx, dy = x - center_x, y - center_y
                    distance = math.sqrt(dx*dx + dy*dy) / radius
                    
                    if distance < 1.0:
                        # Calculamos el falloff (atenuación) basado en la distancia
                        falloff = max(0, 1.0 - distance*distance)
                        falloff = falloff ** 0.5  # Aplica una curva para suavizar
                        
                        alpha = int(intensity * falloff)
                        alpha = max(0, min(255, alpha))
                        
                        # Obtenemos el color actual del pixel
                        current = self.light_surface.get_at((x, y))
                        
                        # Reducimos la opacidad (oscuridad) por el valor de alpha
                        new_alpha = max(0, current[3] - alpha)
                        
                        # Establecemos el nuevo color con transparencia reducida
                        self.light_surface.set_at((x, y), (current[0], current[1], current[2], new_alpha))
        
        # Aplicamos la superficie de luz sobre la superficie principal
        surface.blit(self.light_surface, (0, 0))
