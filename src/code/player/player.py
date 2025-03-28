"""Class representing the player with animations and movement."""

import pygame
import os


class Player(pygame.sprite.Sprite):
    """Handles the logic and animations of the player."""

    def __init__(self, pos, animation_paths, speed=5, scale=1.0):
        """Initializes the player with position and animations."""
        super().__init__()
        self.base_speed = speed
        self.speed = speed
        self.scale = scale  
        self.animation_frames = {}
        self.animation_speeds = {
            'idle': 0.125,      
            'walking': 0.125,  
            'attack': 0.15,    # Speed for attack animation
        }
        self.debug = False
        self.load_animations(animation_paths)
        self.current_animation = 'idle'
        self.frame_index = 0
        self.animation_timer = 0
        self.direction = pygame.math.Vector2(0, 0)
        self.facing_right = True
        
        # Add a flag to control interaction animation
        self.is_interacting = False
        self.interaction_timer = 0
        self.interaction_duration = 0  # No longer used, now controlled by frames
        
        # Store the total number of frames in the attack animation
        # to know when it ends
        self.attack_frames_total = 0
        self.attack_frame_current = 0
        
        # Gameplay attributes
        self.influence_percentage = 0.0  # Inicializar en 40% para tener más luz al comenzar
        self.energy_percentage = 100.0   # Starts at 100%
        self.critical_influence_threshold = 87.0  # When reached, NPCs start rejecting
        self.energy_decay_rate = 0.5     # How fast energy decays passively per second
        self.energy_decay_multiplier = 1.0  # Used to increase decay rate on rejection
        self.convinced_npcs_count = 0    # Count of NPCs successfully convinced
        self.special_ending_triggered = False  # Flag for the special ending
        self.game_over = False  # Flag to indicate if the game is over
        
        # Conviction rate (ability to convince NPCs)
        self.conviction_rate = 0.5  # Initial conviction rate (50%)
        self.min_conviction_rate = 0.1   # Minimum conviction rate
        self.max_conviction_rate = 0.9   # Maximum conviction rate
        
        # Nuevas variables para control de estado global
        self.threshold_exceeded = False  # Si ya se superó el umbral crítico
        self.passive_energy_drain = 0.5  # Para el drenaje pasivo de energía
        self.is_movement_locked = False  # Para controlar si el jugador puede moverse
        
        if self.current_animation in self.animation_frames and len(self.animation_frames[self.current_animation]) > 0:
            self.image = self.animation_frames[self.current_animation][0]['original']
        else:
            # Create a fallback image if animations aren't loaded
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255))  # Magenta for visibility
            
        self.rect = self.image.get_rect(center=pos)

    def load_animations(self, animation_paths):
        """Loads animations from files."""
        for animation_name, path in animation_paths.items():
            frames = []
            
            # Safety check for path existence
            if not os.path.exists(path):
                print(f"Warning: Animation path does not exist: {path}")
                continue
                
            try:
                files = [f for f in sorted(os.listdir(path)) if os.path.isfile(os.path.join(path, f))]
                
                for frame_name in files:
                    frame_path = os.path.join(path, frame_name)

                    try:
                        frame_image = pygame.image.load(frame_path).convert_alpha()

                        if self.scale != 1.0:
                            width = int(frame_image.get_width() * self.scale)
                            height = int(frame_image.get_height() * self.scale)
                            frame_image = pygame.transform.scale(frame_image, (width, height))
                            

                        frames.append({
                            'original': frame_image,
                            'flipped': pygame.transform.flip(frame_image, True, False)
                        })
                        
                    except Exception as e:
                        print(f"Error loading frame {frame_path}: {e}")

                if frames:
                    self.animation_frames[animation_name] = frames
                    if self.debug:
                        print(f"Loaded {len(frames)} frames for {animation_name}")
                    if animation_name == 'attack':
                        self.attack_frames_total = len(frames)
                else:
                    print(f"Warning: No frames loaded for animation: {animation_name}")
                    
            except Exception as e:
                print(f"Error processing animation {animation_name}: {e}")
        
        # Create a placeholder if no animations were loaded
        if not self.animation_frames:
            placeholder = pygame.Surface((32, 32))
            placeholder.fill((255, 0, 255))  # Magenta for visibility
            self.animation_frames['idle'] = [{'original': placeholder, 'flipped': placeholder}]
            print("Warning: No animations loaded. Using placeholder.")
            
        for anim_name in self.animation_frames:
            if anim_name not in self.animation_speeds:
                self.animation_speeds[anim_name] = 0.1  # Default speed
                print(f"Set default speed for animation: {anim_name}")

    def get_current_animation_speed(self):
        """Returns the speed for the current animation."""
        return self.animation_speeds.get(self.current_animation, 0.1)  # Default to 0.1 if not found

    def animate(self, dt):
        """Updates the player's animation frames."""
        if self.current_animation not in self.animation_frames:
            print(f"Warning: Animation '{self.current_animation}' not available")
            return
            
        current_speed = self.get_current_animation_speed()
            
        self.animation_timer += dt
        frames_count = len(self.animation_frames[self.current_animation])
        
        if self.animation_timer >= current_speed:
            while self.animation_timer >= current_speed:
                self.animation_timer -= current_speed
                
                # Handle attack animation specifically
                if self.is_interacting and self.current_animation == 'attack':
                    # Increment attack animation frame counter
                    self.attack_frame_current += 1
                    
                    # Move to the next frame, but do not cycle if it's an attack
                    if self.frame_index < frames_count - 1:
                        self.frame_index += 1
                    else:
                        # Attack animation has ended, switch back to idle
                        self.is_interacting = False
                        self.set_animation('idle')
                        break
                else:
                    # For other animations, cycle normally
                    self.frame_index = (self.frame_index + 1) % frames_count
                
            # Update the image based on direction
            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['original']
            else:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['flipped']
                
            if self.debug:
                print(f"Animation: {self.current_animation}, Frame: {self.frame_index}, Speed: {current_speed}, Timer: {self.animation_timer:.3f}")

    def update(self, dt):
        """Updates the player's position and animation."""
        dt = max(dt, 0.001)
        
        # Update interaction timer if interacting
        if self.is_interacting:
            self.interaction_timer += dt
            if self.interaction_timer >= self.interaction_duration:
                # End interaction when time is up
                self.is_interacting = False
                # Switch back to idle animation
                self.set_animation('idle')
                # Do not restore previous direction to prevent automatic movement after interaction
        
        # Update animation
        self.animate(dt)
        
        # Do not allow movement if interacting
        if not self.is_interacting:
            # Update position
            if self.direction.length() > 0:
                normalized_dir = self.direction.normalize()
                # Calculate the full movement first
                move_x = normalized_dir.x * self.speed * dt
                move_y = normalized_dir.y * self.speed * dt
                
                # Store the position as a float for higher precision
                if not hasattr(self, '_float_pos'):
                    self._float_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
                
                # Update the float position
                self._float_pos.x += move_x
                self._float_pos.y += move_y
                
                # Update the position in the rect (with rounding)
                self.rect.x = round(self._float_pos.x)
                self.rect.y = round(self._float_pos.y)

    def set_animation(self, animation_name):
        """Changes the player's current animation."""
        # Only change if the animation exists and is different
        if (animation_name in self.animation_frames and 
            self.current_animation != animation_name):
            
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_timer = 0

            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][0]['original']
            else:
                self.image = self.animation_frames[self.current_animation][0]['flipped']
                
            if self.debug:
                print(f"Changed animation to: {animation_name}")

    def move(self, direction):
        """Moves the player in a specific direction."""
        # Store previous direction to detect changes
        prev_direction = self.direction.copy()
        
        # Update direction
        self.direction = direction.copy()
        
        # Update animation based on movement state
        if self.direction.length() > 0:
            self.set_animation('walking')
            
            if self.direction.x > 0:
                self.facing_right = True
            elif self.direction.x < 0:
                self.facing_right = False
        else:
            self.set_animation('idle')
            
        # Force image update if direction changed
        if prev_direction != self.direction:
            frames = self.animation_frames[self.current_animation]
            if self.facing_right:
                self.image = frames[self.frame_index]['original']
            else:
                self.image = frames[self.frame_index]['flipped']

    def attack(self):
        """Starts the attack animation and locks player movement temporarily."""
        self.set_animation('attack')
        self.is_interacting = True
        self.interaction_timer = 0
        # Initialize attack frame counter
        self.attack_frame_current = 0
        # Store previous direction
        self.saved_direction = self.direction.copy()
        # Stop the player during interaction
        self.direction = pygame.math.Vector2(0, 0)

    def set_animation_speed(self, animation_name, speed):
        """Sets the speed for a specific animation."""
        if animation_name in self.animation_speeds:
            self.animation_speeds[animation_name] = speed
            
    def set_all_animation_speeds(self, speed_dict):
        """Sets speeds for multiple animations at once.
        
        Args:
            speed_dict: Dictionary mapping animation names to speed values
        """
        for anim_name, speed in speed_dict.items():
            self.animation_speeds[anim_name] = speed

    def force_center_position(self, screen_width, screen_height):
        """Forces the player's position to the exact center of the screen.
        
        This method is called when switching to full screen or resizing the window.
        """
        # Set the center of the player's rect to the center of the screen
        self.rect.center = (screen_width // 2, screen_height // 2)
        
        # Also update the float position to maintain consistency
        if hasattr(self, '_float_pos'):
            self._float_pos.x = self.rect.x
            self._float_pos.y = self.rect.y
            
        # Reset the direction to avoid unwanted sliding
        self.direction = pygame.math.Vector2(0, 0)
            
    def update_gameplay_stats(self, dt, rejected=False):
        """Updates gameplay-related stats like energy depletion, conviction rate effects, etc.
        
        Args:
            dt: Time elapsed since last frame
            rejected: Whether the player was rejected by an NPC
        """
        # Solo actualizar si el juego no ha terminado
        if not self.game_over:
            # Actualizar la influencia y la energía basadas en el tiempo
            influence_factor = 1.0
            
            # Aplicar el drenaje pasivo de energía
            if not self.is_movement_locked:
                # Passive energy drain - scale by influence
                energy_loss = self.passive_energy_drain * dt * influence_factor
                if self.threshold_exceeded:
                    # Drenaje de energía incrementado si se superó el umbral
                    energy_loss *= 2.0
                
                self.decrease_energy(energy_loss)
            
            # Verificar condiciones de fin de juego
            if self.energy_percentage <= 0:
                self.energy_percentage = 0
                self.game_over = True
                
                # Determinar el tipo de final basado en si se superó el umbral crítico
                if self.threshold_exceeded:
                    self.special_ending_triggered = True  # Final pantalla blanca
                else:
                    # Final pantalla azul (energía a 0 sin superar umbral)
                    self.special_ending_triggered = False
            
            # Si la influencia llega a 0 después de haber superado el umbral, también termina el juego
            if self.threshold_exceeded and self.influence_percentage <= 0:
                self.influence_percentage = 0
                self.game_over = True
                self.special_ending_triggered = True  # Final pantalla blanca

    def update_influence(self, amount):
        """Updates the player's influence percentage."""
        old = self.influence_percentage
        self.influence_percentage = max(0, min(100, self.influence_percentage + amount))
        
        if self.influence_percentage >= self.critical_influence_threshold:
            self.threshold_exceeded = True
            self.conviction_rate = 0  # Bloquear convicción
        
        return self.influence_percentage

    def update_energy(self, amount):
        """Updates the player's energy percentage."""
        # In this case, we are always consuming energy (negative value)
        self.energy_percentage = max(0.0, min(100.0, self.energy_percentage + amount))
        
        # Check for game over
        if self.energy_percentage <= 0 and not self.game_over:
            self.game_over = True
            
        return self.energy_percentage

    def increase_influence(self, amount):
        """Increases the player's influence percentage."""
        return self.update_influence(amount)
        
    def decrease_energy(self, amount):
        """Decreases the player's energy percentage."""
        return self.update_energy(-amount)

    def get_conviction_rate(self):
        """Returns the player's current conviction rate (0.0 to 1.0).
        
        Returns:
            float: The player's conviction rate between 0.1 and 0.9
        """
        return self.conviction_rate
        
    def increase_conviction_rate(self, amount):
        """Increases the player's conviction rate."""
        # Ensure conviction rate stays within limits
        self.conviction_rate = min(self.max_conviction_rate, self.conviction_rate + amount)
        return self.conviction_rate
        
    def decrease_conviction_rate(self, amount):
        """Decreases the player's conviction rate."""
        # Ensure conviction rate stays within limits
        self.conviction_rate = max(self.min_conviction_rate, self.conviction_rate - amount)
        return self.conviction_rate

    def draw_stats(self, screen, scale=1.0):
        """Draws the player's influence and energy bars.
        
        Args:
            screen: Surface to draw on
            scale: UI scale factor
        """
        # Constants for bar dimensions and positions
        bar_width = int(300 * scale)  # Wider bars (previously 200)
        bar_height = int(15 * scale)  # Taller bars (previously 10)
        padding = int(20 * scale)  # More padding
        corner_radius = int(5 * scale)  # More rounded corners
        
        # Position the bars in the bottom left corner
        screen_width, screen_height = screen.get_size()
        x_pos = padding
        y_base = screen_height - padding - (2 * bar_height) - 10  # Base for both bars
        
        # Labels for the bars
        font_size = int(16 * scale)
        try:
            font = pygame.font.SysFont('Arial', font_size)
            influence_label = font.render('Influence', True, (255, 255, 255))
            energy_label = font.render('Energy', True, (255, 255, 255))
        except Exception as e:
            print(f"Error loading font: {e}")
            influence_label = None
            energy_label = None
        
        # Draw influence bar (purple gradient)
        influence_y = y_base
        
        # Background for influence bar
        pygame.draw.rect(
            screen, 
            (40, 40, 40, 200), 
            (x_pos, influence_y, bar_width, bar_height),
            border_radius=corner_radius
        )
        
        # Fill for influence bar (gradient from dark purple to light purple)
        fill_width = int((self.influence_percentage / 100) * bar_width)
        if fill_width > 0:
            influence_surface = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            for i in range(fill_width):
                alpha = i / fill_width
                color = (
                    int(100 + 155 * alpha),  # R
                    int(50 + 50 * alpha),    # G
                    int(150 + 105 * alpha),  # B
                    200                       # A
                )
                pygame.draw.line(influence_surface, color, (i, 0), (i, bar_height))
            
            screen.blit(influence_surface, (x_pos, influence_y))
            
            # Add rounded corners
            pygame.draw.rect(
                screen, 
                (0, 0, 0, 0), 
                (x_pos, influence_y, fill_width, bar_height),
                border_radius=corner_radius
            )
        
        # Draw percentage text
        if influence_label:
            screen.blit(influence_label, (x_pos, influence_y - font_size - 5))
            percentage_text = font.render(f"{int(self.influence_percentage)}%", True, (255, 255, 255))
            text_x = x_pos + bar_width + 10
            text_y = influence_y + (bar_height - percentage_text.get_height()) // 2
            screen.blit(percentage_text, (text_x, text_y))
        
        # Draw energy bar (golden gradient)
        energy_y = influence_y + bar_height + int(10 * scale)
        
        # Background for energy bar
        pygame.draw.rect(
            screen, 
            (40, 40, 40, 200), 
            (x_pos, energy_y, bar_width, bar_height),
            border_radius=corner_radius
        )
        
        # Fill for energy bar (gradient from dark gold to light gold)
        fill_width = int((self.energy_percentage / 100) * bar_width)
        if fill_width > 0:
            energy_surface = pygame.Surface((fill_width, bar_height), pygame.SRCALPHA)
            for i in range(fill_width):
                alpha = i / fill_width
                color = (
                    int(180 + 75 * alpha),   # R
                    int(120 + 135 * alpha),  # G
                    int(20 + 50 * alpha),    # B
                    200                       # A
                )
                pygame.draw.line(energy_surface, color, (i, 0), (i, bar_height))
            
            screen.blit(energy_surface, (x_pos, energy_y))
            
            # Add rounded corners for energy bar
            pygame.draw.rect(
                screen, 
                (0, 0, 0, 0), 
                (x_pos, energy_y, fill_width, bar_height),
                border_radius=corner_radius
            )
        
        # Draw percentage text for energy
        if energy_label:
            screen.blit(energy_label, (x_pos, energy_y - font_size - 5))
            percentage_text = font.render(f"{int(self.energy_percentage)}%", True, (255, 255, 255))
            text_x = x_pos + bar_width + 10
            text_y = energy_y + (bar_height - percentage_text.get_height()) // 2
            screen.blit(percentage_text, (text_x, text_y))