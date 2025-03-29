"""Class representing the player with animations and movement."""

import pygame
import os

# Importar la variable global
from src.code.npc.npc import THRESHOLD_REACHED


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
        self.interaction_duration = 0
        
        # Store the total number of frames in the attack animation
        # to know when it ends
        self.attack_frames_total = 0
        self.attack_frame_current = 0
        
        # Gameplay attributes
        self.influence_percentage = 0.0  # Starts at 0%
        self.energy_percentage = 100.0   # Starts at 100%
        self.critical_influence_threshold = 87.0  
        self.energy_decay_rate = 0.15  
        self.energy_decay_multiplier = 0.8  
        self.convinced_npcs_count = 0   
        self.special_ending_triggered = False 
        self.game_over = False  

        if self.current_animation in self.animation_frames and len(self.animation_frames[self.current_animation]) > 0:
            self.image = self.animation_frames[self.current_animation][0]['original']
        else:
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 0, 255))
            
        self.rect = self.image.get_rect(center=pos)

    def load_animations(self, animation_paths):
        """Loads animations from files."""
        for animation_name, path in animation_paths.items():
            frames = []
            
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
                    self.attack_frame_current += 1
                    
                    if self.frame_index < frames_count - 1:
                        self.frame_index += 1
                    else:
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
        """Updates the player's gameplay statistics.
        
        Args:
            dt: Time elapsed since last frame in seconds
            rejected: Whether the player was just rejected by an NPC
        """
        global THRESHOLD_REACHED
        
        # Check if critical threshold has been reached
        if self.influence_percentage >= self.critical_influence_threshold:
            THRESHOLD_REACHED = True
        
        decay_rate = self.energy_decay_rate
        
        if rejected or THRESHOLD_REACHED:
            decay_rate *= self.energy_decay_multiplier
            
            # Gradually increase decay multiplier after threshold
            if THRESHOLD_REACHED:
                self.energy_decay_multiplier = min(2.0, self.energy_decay_multiplier + 0.03)
        
        self.energy_percentage = max(0.0, self.energy_percentage - (decay_rate * dt))
        
        # If threshold reached, decrease influence over time
        if THRESHOLD_REACHED:
            influence_decay_rate = decay_rate * 0.5
            self.influence_percentage = max(0.0, self.influence_percentage - (influence_decay_rate * dt))
        
        if self.energy_percentage <= 0 and not self.game_over:
            self.game_over = True
            
    def update_influence(self, amount):
        """Updates the player's influence percentage (positive to increase, negative to decrease).
        
        Args:
            amount: Amount to adjust influence (percentage points)
        """
        old_influence = self.influence_percentage
        self.influence_percentage = max(0.0, min(100.0, self.influence_percentage + amount))
        
        # If it's a positive increase, it might mean an NPC was convinced
        if amount > 0:
            # Increment convinced NPCs counter (only if it's a significant increase)
            if amount >= 5.0:
                self.convinced_npcs_count += 1
        
        # Check if we have crossed the critical threshold
        if old_influence < self.critical_influence_threshold and self.influence_percentage >= self.critical_influence_threshold:
            self.energy_decay_multiplier = 2.0  # Start consuming energy faster
            
        return self.influence_percentage
        
    def update_energy(self, amount):
        """Updates the player's energy percentage (positive to add, negative to consume).
        
        Args:
            amount: Amount to adjust energy (percentage points)
        """
        # Update energy (negative values increase energy, positive values decrease it)
        self.energy_percentage = max(0.0, min(100.0, self.energy_percentage - amount))  # Limit to maximum 100%
        
        # Check for game over
        if self.energy_percentage <= 0 and not self.game_over:
            self.game_over = True
            
        return self.energy_percentage

    def increase_influence(self, amount):
        """Increases the player's influence percentage.
        
        Args:
            amount: Amount to increase the influence by (percentage points)
        """
        return self.update_influence(amount)
        
    def decrease_energy(self, amount):
        """Decreases the player's energy percentage.
        
        Args:
            amount: Amount to decrease the energy by (percentage points)
        """
        return self.update_energy(amount)

    def get_conviction_rate(self):
        """
        Returns the player's conviction rate, which determines how effective they are 
        at convincing NPCs. Based on the player's influence percentage.
        
        Returns:
            float: A value between 0.1 and 0.9 that represents the conviction ability.
        """
        # Normalize influence to be between 0.1 and 0.9
        # More influence = higher conviction ability
        base_rate = 0.5  # Base rate
        
        # Add a bonus based on influence (up to +0.4)
        influence_bonus = min(0.4, self.influence_percentage / 100.0 * 0.4)
        
        # Reduce effectiveness if energy is low
        energy_penalty = 0.0
        if self.energy_percentage < 40:
            energy_penalty = 0.3 * (1 - self.energy_percentage / 40.0)
        
        conviction_rate = base_rate + influence_bonus - energy_penalty
        
        # Ensure it's within the range [0.1, 0.9]
        return max(0.1, min(0.9, conviction_rate))
        
    def draw_stats(self, screen, scale=1.0):
        """Draws the player's influence and energy bars.
        
        Args:
            screen: Surface to draw on
            scale: UI scale factor
        """

        bar_width = int(300 * scale) 
        bar_height = int(15 * scale) 
        padding = int(20 * scale) 
        corner_radius = int(5 * scale)
        
        # Position the bars in the bottom left corner
        screen_width, screen_height = screen.get_size()
        x_pos = padding
        y_base = screen_height - padding - (2 * bar_height) - 10  # Base for both bars
        
        # Labels for the bars
        font_size = int(16 * scale)
        try:
            font = pygame.font.Font('./src/assets/fonts/SpecialElite-Regular.ttf', font_size)
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