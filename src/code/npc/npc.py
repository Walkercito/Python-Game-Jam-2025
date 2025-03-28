"""Class representing NPCs with animations and automatic movement."""

import pygame
import os
import random


class NPC(pygame.sprite.Sprite):
    """Handles the logic and animations of NPCs."""

    def __init__(self, pos, animation_paths, speed=120, scale=0.5, direction=1):
        """Initializes a new NPC with the given parameters."""
        super().__init__()

        self.state = random.choice(["CLOSED", "INDECISIVE", "RECEPTIVE"])
        self.animation_paths = animation_paths
        self.animations = {}
        self.scale = scale
        self.debug = False
        
        self.rect = pygame.Rect(pos[0], pos[1], 32, 64)  # Rectangle for the NPC
        self._float_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.direction = pygame.math.Vector2(direction, 0)
        self.facing_right = direction > 0
        self.speed = speed  # Use the speed passed as a parameter (120 by default)
        self.new_scale = scale  # For animations
        
        # Interaction variables
        self.is_interacting = False
        self.can_interact = False
        self.interaction_timer = 0
        self.interaction_duration = 5.0  # 5 seconds of interaction
        self.convinced = False
        
        # Animation
        self.current_animation = "walking"
        self.animation_index = 0
        self.animation_speed = 0.15
        self.animation_timer = 0
        self.animation_played = False
        
        # New variable to control the animation sequence
        self.animation_sequence = []
        self.current_sequence_index = 0
        
        # Collision system
        self.collision_rect = pygame.Rect(0, 0, self.rect.width - 20, self.rect.height)
        self.collision_cooldown = 0
        
        # Anti-blocking system
        self.can_change_direction = True
        self.direction_change_cooldown = 0
        self.direction_change_chance = 0.001  # Reasonable probability
        
        # Simplified anti-blocking system
        self.stuck_timer = 0
        self.stuck_threshold = 8.0  # Longer time to be sure it's stuck
        self.last_position = pygame.math.Vector2(pos)
        self.movement_threshold = 10  # Minimum distance to consider real movement
        
        # Internal conviction state
        self.current_indecisive_rate = 0.3
        self.current_closed_rate = 0.3
        
        # For off-screen tracking
        self.time_offscreen = 0
        self.offscreen_limit = 2.0
        
        # Interaction indicator
        self.interaction_indicator = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        # Load animations and set initial image
        self.load_animations()
        
        # Initialize image (temporary until animations are loaded)
        if self.animations.get(self.current_animation):
            self.image = self.animations[self.current_animation][0]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            # Fallback if no animations are loaded
            self.image = pygame.Surface((32, 64))
            self.image.fill(self.get_color_by_state())
            
        # Update interaction indicator
        self.update_interaction_indicator()
        
    def load_animations(self):
        """Loads animations from files."""
        for animation_name, path in self.animation_paths.items():
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
                            
                        frames.append(frame_image)
                        
                    except Exception as e:
                        print(f"Error loading frame {frame_path}: {e}")

                if frames:
                    self.animations[animation_name] = frames
                    
                    # Update rectangle size based on the first frame of the "walking" animation
                    if animation_name == "walking" and not self.animations.get("walking"):
                        self.rect.width = frames[0].get_width()
                        self.rect.height = frames[0].get_height()
                        
                    if self.debug:
                        print(f"Loaded {len(frames)} frames for {animation_name}")
                else:
                    print(f"Warning: No frames loaded for animation: {animation_name}")
                    
            except Exception as e:
                print(f"Error processing animation {animation_name}: {e}")
        
        # Create a placeholder if no animations were loaded
        if not self.animations:
            placeholder = pygame.Surface((32, 64))
            placeholder.fill(self.get_color_by_state())
            self.animations['idle'] = [placeholder]
            self.animations['walking'] = [placeholder]
            print("Warning: No animations loaded for NPC. Using placeholder.")
        
        # Ensure the rectangle has the correct size based on the walking animation
        if self.animations.get("walking"):
            first_frame = self.animations["walking"][0]
            self.rect.width = first_frame.get_width()
            self.rect.height = first_frame.get_height()
            # Keep the center position
            center = self.rect.center
            self.rect.size = (first_frame.get_width(), first_frame.get_height())
            self.rect.center = center
        
    def get_color_by_state(self):
        """Returns a color based on the NPC's state."""
        if self.state == "CLOSED":
            return (255, 50, 50)  # Red for closed
        elif self.state == "INDECISIVE":
            return (255, 255, 50)  # Yellow for indecisive
        else:
            return (50, 255, 50)   # Green for receptive

    def update_interaction_indicator(self):
        """Update the interaction indicator color based on NPC state."""
        self.interaction_indicator = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        if self.state == "CLOSED":
            color = (255, 50, 50, 200)  # Red for closed
        elif self.state == "INDECISIVE":
            color = (255, 255, 50, 200)  # Yellow for indecisive
        else:
            color = (50, 255, 50, 200)  # Green for receptive
            
        pygame.draw.circle(self.interaction_indicator, color, (12, 12), 8)
        
    def animate(self, dt):
        """Updates the NPC's current animation frame."""
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            # If we are in an animation sequence
            if self.animation_sequence:
                # Advance the current animation
                animation_frames = self.animations[self.current_animation]
                self.animation_index = (self.animation_index + 1) % len(animation_frames)
                
                # If we finished the current animation
                if self.animation_index == 0:
                    # Mark that it has been played
                    self.animation_played = True
                    
                    # Advance to the next animation in the sequence
                    self.current_sequence_index += 1
                    
                    # If there are still more animations in the sequence
                    if self.current_sequence_index < len(self.animation_sequence):
                        self.current_animation = self.animation_sequence[self.current_sequence_index]
                        self.animation_index = 0
                    else:
                        # End of the sequence, go back to walking or idle based on the state
                        self.animation_sequence = []
                        self.current_sequence_index = 0
                        
                        if self.convinced:
                            # If it was convinced, walk out of the screen
                            self.current_animation = "walking"
                        else:
                            # If it was not convinced, go back to walking normally
                            self.current_animation = "walking"
            else:
                # Normal animation without sequence
                animation_frames = self.animations[self.current_animation]
                self.animation_index = (self.animation_index + 1) % len(animation_frames)
                
            # Update the current image
            self.image = self.animations[self.current_animation][self.animation_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)
        
    def set_animation(self, animation_name):
        """Changes the current animation to the specified one."""
        if animation_name in self.animations:
            self.current_animation = animation_name
            self.animation_index = 0
            self.animation_played = False

    def set_animation_sequence(self, sequence):
        """Sets an animation sequence to play in order."""
        valid_sequence = [anim for anim in sequence if anim in self.animations]
        if valid_sequence:
            self.animation_sequence = valid_sequence
            self.current_sequence_index = 0
            self.current_animation = self.animation_sequence[0]
            self.animation_index = 0
            self.animation_played = False
        
    def update(self, dt, screen_width, camera=None, other_npcs=None):
        """Updates the NPC's position and animation."""
        dt = max(dt, 0.001)
        self.animate(dt)
        
        # Update cooldowns
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
            
        if self.direction_change_cooldown > 0:
            self.direction_change_cooldown -= dt
            if self.direction_change_cooldown <= 0:
                self.can_change_direction = True
        
        # Interaction system
        if self.is_interacting:
            self.interaction_timer += dt
            if self.interaction_timer >= self.interaction_duration:
                self.is_interacting = False
                self.interaction_timer = 0
                
                # Only reset if there is no active sequence
                if not self.animation_sequence:
                    self.set_animation('walking')
                
                self.animation_played = False
            return  # Don't move while interacting
        
        # Simplified anti-blocking system
        current_pos = pygame.math.Vector2(self.rect.center)
        distance_moved = current_pos.distance_to(self.last_position)
        
        if distance_moved < self.movement_threshold:
            self.stuck_timer += dt
            # Only intervene if it's really stuck for a long time
            if self.stuck_timer > 8.0:  # Longer time to be sure it's stuck
                self._float_pos.x += self.direction.x * 20  # Only a push in the current direction
                self.rect.x = round(self._float_pos.x)
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.last_position = current_pos
        
        # Random direction change (normal probability)
        if self.can_change_direction and random.random() < 0.001:  # Reasonable probability
            self.change_direction()
            self.can_change_direction = False
            self.direction_change_cooldown = 3.0  # Moderate cooldown
        
        # Check for collisions with other NPCs - only if the cooldown has expired
        if other_npcs and self.collision_cooldown <= 0:
            self.check_collision(other_npcs)
        
        # Normal movement
        if self.direction.length() > 0:
            move_x = self.direction.x * self.speed * dt
            
            # If the NPC has been convinced, make sure it heads out of the screen
            if self.convinced:
                # Determine which screen edge is faster to exit
                if camera:
                    screen_left = camera.offset.x
                    screen_right = camera.offset.x + screen_width
                    
                    # If it's closer to the left edge, go left
                    if self.rect.centerx - screen_left < screen_right - self.rect.centerx:
                        if self.direction.x > 0:  # If going right, turn around
                            self.direction.x = -1
                            self.facing_right = False
                    else:  # Closer to the right edge, go right
                        if self.direction.x < 0:  # If going left, turn around
                            self.direction.x = 1
                            self.facing_right = True
                else:
                    # Version without camera
                    if self.rect.centerx < screen_width / 2:
                        if self.direction.x > 0:
                            self.direction.x = -1
                            self.facing_right = False
                    else:
                        if self.direction.x < 0:
                            self.direction.x = 1
                            self.facing_right = True
                
                # Increase speed to exit faster
                move_x = self.direction.x * self.speed * 1.5 * dt
            
            self._float_pos.x += move_x
            self.rect.x = round(self._float_pos.x)
            is_offscreen = False
            
            if camera:
                # Calculate screen limits based on the camera
                screen_left = camera.offset.x
                screen_right = camera.offset.x + screen_width
                
                # Check if the NPC is more than 40px off-screen
                if (self.rect.right < screen_left - 40) or (self.rect.left > screen_right + 40):
                    is_offscreen = True
            else:
                if self.rect.right < -40 or self.rect.left > screen_width + 40:
                    is_offscreen = True
            
            # Update off-screen time
            if is_offscreen:
                # Only allow convinced NPCs to exit the screen
                if self.convinced:
                    self.time_offscreen += dt
                    if self.time_offscreen >= self.offscreen_limit:
                        self.kill()  # Remove NPC if off-screen for too long
                else:
                    # If not convinced, change its direction to go back on-screen
                    self.change_direction()
                    # Move the NPC back on-screen
                    if camera:
                        if self.rect.right < screen_left:
                            self._float_pos.x = screen_left - self.rect.width * 0.5
                        elif self.rect.left > screen_right:
                            self._float_pos.x = screen_right - self.rect.width * 0.5
                    else:
                        if self.rect.right < 0:
                            self._float_pos.x = -self.rect.width * 0.5
                        elif self.rect.left > screen_width:
                            self._float_pos.x = screen_width - self.rect.width * 0.5
                    self.rect.x = round(self._float_pos.x)
            else:
                self.time_offscreen = 0
        
        # Update the collision rectangle position
        self.collision_rect.center = self.rect.center

    def change_direction(self):
        """Changes the NPC's direction."""
        self.direction.x *= -1
        self.facing_right = not self.facing_right

    def check_collision(self, other_npcs):
        """Checks and handles collisions with other NPCs."""
        if self.collision_cooldown > 0:
            return False
            
        self.collision_rect.center = self.rect.center
        collision_occurred = False
        
        for npc in other_npcs:
            if npc != self and not npc.is_interacting:
                npc.collision_rect.center = npc.rect.center
                
                # Check for collision
                if self.collision_rect.colliderect(npc.collision_rect):
                    # Simply separate without changing direction
                    my_pos = pygame.math.Vector2(self.rect.center)
                    other_pos = pygame.math.Vector2(npc.rect.center)
                    
                    # Separation vector
                    separation = my_pos - other_pos
                    if separation.length() > 0:
                        separation.normalize_ip()
                        # Apply smooth separation
                        self._float_pos.x += separation.x * 10
                        self._float_pos.y += separation.y * 3
                    
                    # Update position
                    self.rect.x = round(self._float_pos.x)
                    self.rect.y = round(self._float_pos.y)
                    
                    # Small cooldown
                    self.collision_cooldown = 0.5
                    collision_occurred = True
        
        return collision_occurred

    def interact(self, player=None):
        """Player interacts with this NPC.
        
        Returns:
            bool: True if interaction was successful
        """
        if not self.is_interacting:
            self.is_interacting = True
            
            # Set an animation sequence based on the type of NPC
            convincing_result = None
            player_conviction = player.get_conviction_rate() if player else 0.5
            
            # Verificar si el jugador ha superado el umbral crítico
            player_influence = player.influence_percentage if player and hasattr(player, 'influence_percentage') else 0
            critical_threshold = player.critical_influence_threshold if hasattr(player, 'critical_influence_threshold') else 87.0
            player_energy = player.energy_percentage if player and hasattr(player, 'energy_percentage') else 100.0
            
            # Variable para marcar si se ha superado el umbral crítico
            threshold_exceeded = player_influence >= critical_threshold
            
            # Cuando el jugador está por encima del umbral crítico:
            # 1. Forzar convicción a 0 (no puede convencer a nadie)
            # 2. Todos los NPCs pasan a estado CLOSED
            if threshold_exceeded:
                player.conviction_rate = 0  # Fuerza la convicción a cero
                self.state = "CLOSED"
                self.update_interaction_indicator()  # Actualizar color
            
            # Calculate the probability of successful conviction
            if player:
                if threshold_exceeded:
                    convincing_result = False
                    
                    # Pérdida de energía fija por interacción
                    energy_loss = -10.0
                    
                    # Calcular interacciones restantes basadas en energía
                    remaining_interactions = max(1, player_energy / abs(energy_loss))
                    
                    # Calcular pérdida de influencia proporcional
                    influence_loss = -player_influence / remaining_interactions
                    
                    # Aplicar pérdidas SIN límites mínimos/máximos
                    player.update_energy(energy_loss)
                    player.update_influence(influence_loss)
                    
                elif self.state == "RECEPTIVE":
                    # Si el jugador está por encima del umbral crítico, siempre es rechazado
                    if threshold_exceeded:
                        convincing_result = False
                    else:
                        convincing_result = random.random() < 0.7 + (player_conviction * 0.3)
                    # Lower energy cost for receptive NPCs
                    player.update_energy(-2.5)
                    # Add energy recovery when convincing a receptive NPC
                    if convincing_result:
                        player.update_energy(7.0)
                        # Increase conviction rate for successful interaction
                        player.increase_conviction_rate(0.02)
                    else:
                        # Decrease conviction rate for being rejected
                        player.decrease_conviction_rate(0.01)
                        # Decrease influence when rejected
                        player.update_influence(-0.5)
                elif self.state == "INDECISIVE":
                    # Si el jugador está por encima del umbral crítico, siempre es rechazado
                    if threshold_exceeded:
                        convincing_result = False
                    else:
                        convincing_result = random.random() < 0.4 + (player_conviction * 0.3)
                    # Medium energy cost for indecisive NPCs
                    player.update_energy(-3.5)
                    # Add energy recovery when convincing an indecisive NPC
                    if convincing_result:
                        player.update_energy(5.0)
                        # Increase conviction 
                        player.increase_conviction_rate(0.01)
                    else:
                        # Decrease conviction when rejected
                        player.decrease_conviction_rate(0.02)
                        # Decrease influence when rejected
                        player.update_influence(-0.7)
                else:  # CLOSED
                    # Even in closed state, always reject if influence is too high
                    if threshold_exceeded:
                        convincing_result = False
                    else:
                        convincing_result = random.random() < 0.2 + (player_conviction * 0.3)
                    # Higher energy cost for closed NPCs
                    player.update_energy(-5.0)
                    # Add energy recovery when convincing a closed NPC
                    if convincing_result:
                        player.update_energy(8.0)
                        # Increase conviction for hard success
                        player.increase_conviction_rate(0.03)
                    else:
                        # Higher decrease on rejection
                        player.decrease_conviction_rate(0.03)
                        # Decrease influence when rejected
                        player.update_influence(-1.0)
                
                # Update player stats based on the interaction
                if convincing_result:
                    player.update_influence(5.0)
            
            # Start the animation sequence
            # First "book" animation, then the result animation
            animation_sequence = ["book"]
            
            # Update NPC state based on result
            if convincing_result:
                self.convinced = True
                animation_sequence.append("convinced")
                if self.state != "RECEPTIVE":
                    self.state = "RECEPTIVE"
                    # Update the interaction indicator with the new state
                    self.update_interaction_indicator()
            elif self.state == "INDECISIVE":
                animation_sequence.append("indecisive")
                # There's a chance the NPC becomes more closed
                if random.random() < 0.3:
                    self.state = "CLOSED"
                    # Update the interaction indicator with the new state
                    self.update_interaction_indicator()
            else:
                animation_sequence.append("closed")
            
            # Set the sequence
            self.set_animation_sequence(animation_sequence)
            
            # Reset the interaction timer
            self.interaction_timer = 0
            
            return True

    def get_player(self):
        """Gets the player instance from the manager. To be implemented by manager."""
        # This is just a placeholder - the actual implementation will be in NPCManager
        return None

    def draw_interaction_indicator(self, screen, camera):
        """Draw an indicator when the player can interact with this NPC."""
        if self.can_interact:
            # Place the indicator closer to the NPC (less offset)
            indicator_pos = camera.apply_point((self.rect.centerx + 5, self.rect.top + 5))
            # Center the indicator (12 is half the size of the 24x24 indicator)
            screen.blit(self.interaction_indicator, (indicator_pos[0] - 12, indicator_pos[1] - 12))


class NPCManager:
    """Manages the spawning and updating of NPCs."""
    
    def __init__(self, animation_paths, screen_width, screen_height, player=None):
        """Initialize the NPC manager."""
        self.animation_paths = animation_paths
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.npcs = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        
        self.max_npcs = 23
        
        self.spawn_offset_x = 100 
        
        self.interaction_active = False
        
        self.spawn_zones = []
        self.update_spawn_zones()
        
        self.player = player
        
        # Variable para rastrear si todos los NPCs deben estar en estado CLOSED
        self.all_npcs_closed = False
        
    def update_spawn_zones(self):
        """Updates spawn zones based on screen size."""
        zone_height = 100
        num_zones = max(1, self.screen_height // zone_height)
        
        self.spawn_zones = []
        for i in range(num_zones):
            zone_y = (i * zone_height) + (zone_height // 2)
            self.spawn_zones.append(zone_y)
    
    def get_visible_npcs(self, camera):
        """Returns a list of NPCs that are visible in the current camera view.
        
        Args:
            camera: The camera object used to determine visibility
            
        Returns:
            List of NPC objects currently visible
        """
        visible_npcs = []
        camera_rect = pygame.Rect(0, 0, camera.width, camera.height)
        camera_rect.center = (camera.offset.x + camera.width // 2, camera.offset.y + camera.height // 2)
        
        # Expand camera rect with margin to prevent pop-in
        margin = 100
        camera_rect = camera_rect.inflate(margin * 2, margin * 2)
        
        for npc in self.npcs:
            if camera_rect.colliderect(npc.rect):
                visible_npcs.append(npc)
                
        return visible_npcs
        
    def update(self, dt, player_rect, camera=None):
        """Update all NPCs and spawn new ones."""
        if self.interaction_active:
            if not any(npc.is_interacting for npc in self.npcs):
                self.interaction_active = False
                
        # Verificar si el jugador ha superado el umbral crítico
        if self.player and hasattr(self.player, 'threshold_exceeded') and self.player.threshold_exceeded:
            # Si el jugador superó el umbral, todos los NPCs deben estar en estado CLOSED
            self.all_npcs_closed = True
            
            # Convertir a todos los NPCs existentes a estado CLOSED
            for npc in self.npcs:
                if npc.state != "CLOSED":
                    npc.state = "CLOSED"
                    npc.update_interaction_indicator()
        
        # Update all existing NPCs
        for npc in list(self.npcs):  # Copy the list to avoid modification during iteration
            original_position = pygame.math.Vector2(npc.rect.center)
            
            # Update the NPC
            npc.update(dt, self.screen_width, camera, [other_npc for other_npc in self.npcs if other_npc != npc])
            
            # If NPC is convinced, they will walk off screen
            if npc.convinced:
                # Check if they are far off-screen
                screen_rect = pygame.Rect(0, 0, self.screen_width, camera.height if camera else 600)
                if not screen_rect.colliderect(npc.rect):
                    # Remove this NPC and spawn a replacement
                    self.npcs.remove(npc)
                    self.spawn_npc(camera)
        
        # Spawn new NPCs if needed
        if len(self.npcs) < self.max_npcs:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_interval:
                self.spawn_timer = 0
                self.spawn_npc(camera)
    
    def handle_interaction(self, player_rect, keys):
        """Handle player interaction with NPCs."""
        if self.interaction_active:
            interacting_npcs = [npc for npc in self.npcs if npc.is_interacting]
            if not interacting_npcs:
                self.interaction_active = False
            
        # Mostrar el indicador de interacción solo en el NPC más cercano que está lo suficientemente cerca
        closest_npc = None
        min_distance = float('inf')
        
        for npc in self.npcs:
            if npc.convinced or npc.is_interacting:
                continue  # Skip NPCs that are already convinced
                
            # Calcular la distancia entre el jugador y el NPC
            dx = player_rect.centerx - npc.rect.centerx
            dy = player_rect.centery - npc.rect.centery
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 100 and distance < min_distance:  # Radio de 100 píxeles para interacción
                min_distance = distance
                closest_npc = npc
                
        # Desactivar indicadores en todos los NPCs excepto el más cercano
        for npc in self.npcs:
            npc.can_interact = (npc == closest_npc and not self.interaction_active)
                
        # Activar el indicador solo en el NPC más cercano
        if closest_npc:
            closest_npc.can_interact = True
            
            # Interactuar si se presionó la tecla E
            if closest_npc and keys[pygame.K_e] and not self.interaction_active:
                self.interaction_active = True
                if self.player and hasattr(self.player, 'threshold_exceeded') and self.player.threshold_exceeded:
                    self.player.attack()
                    closest_npc.interact(self.player)
                    return
                
                # Interacción normal
                self.interaction_active = True
                if closest_npc.interact(self.player):  # Si la interacción tuvo éxito
                    closest_npc.convinced = True

    def draw(self, screen, camera):
        """Draw all NPCs and their interaction indicators."""
        # Sort NPCs by Y position for proper Z-index rendering
        npcs_to_draw = sorted(self.npcs.sprites(), key=lambda npc: npc.rect.bottom)
        
        for npc in npcs_to_draw:
            npc_rect = camera.apply(npc.rect)
            screen.blit(npc.image, npc_rect)
            
            npc.draw_interaction_indicator(screen, camera)

    def spawn_npc(self, camera=None):
        """Spawn a new NPC at the right or left edge of the screen."""
        if len(self.npcs) >= self.max_npcs:
            return
        
        speed = random.randint(8, 12) * 10  # Velocidad entre 80-120
        direction = random.choice([-1, 1])
        
        # Define the position offsets based on screen dimensions
        position_x = 0
        if direction > 0:  # Moving to the right
            position_x = -100  # Start off-screen to the left
        else:  # Moving to the left
            position_x = self.screen_width + 100  # Start off-screen to the right
            
        # Choose a random zone to spawn
        zone = random.choice(self.spawn_zones)
        position_y = zone + random.randint(-50, 50)  # El valor de zone es directamente la altura Y
        
        # Adjust position based on camera
        if camera:
            position_x += camera.offset.x
            position_y += camera.offset.y
        
        new_npc = NPC(
            (position_x, position_y),
            self.animation_paths,
            speed=speed,
            scale=0.5,  # Same scale as player
            direction=direction
        )
        
        # Set the player instance for the NPC
        if self.player:
            new_npc.get_player = lambda: self.player
        
        # Si el jugador ha superado el umbral, todos los nuevos NPCs deben estar en estado CLOSED
        if self.all_npcs_closed:
            new_npc.state = "CLOSED"
            new_npc.update_interaction_indicator()
        
        # Check if new NPC is too close to existing NPCs
        for npc in self.npcs:
            dx = new_npc.rect.centerx - npc.rect.centerx
            dy = new_npc.rect.centery - npc.rect.centery
            distance = (dx**2 + dy**2)**0.5
            
            if distance < 100:  # Minimum distance of 100 pixels
                # Try again with a different position
                return self.spawn_npc(camera)
        
        self.npcs.add(new_npc)
        return new_npc

    def respawn_npc(self, npc, camera=None):
        """Repositions an NPC at a random edge of the screen relative to the player."""
        if not npc or npc not in self.npcs:
            return
        
        # Save current states
        current_convinced = npc.convinced
        current_state = npc.state
        
        if camera:
            player_center_x = camera.offset.x + (self.screen_width // 2)
            player_center_y = camera.offset.y + (self.screen_height // 2)
            
            # Only use left and right sides for better distribution
            spawn_side = random.choice([1, 3])  # 1=right, 3=left
            
            if spawn_side == 1:  # Right
                spawn_x = player_center_x + (self.screen_width // 2) + self.spawn_offset_x
                spawn_y = player_center_y + random.randint(-self.screen_height//3, self.screen_height//3)
                new_direction = -1  # Towards the left
            else:  # Left
                spawn_x = player_center_x - (self.screen_width // 2) - self.spawn_offset_x
                spawn_y = player_center_y + random.randint(-self.screen_height//3, self.screen_height//3)
                new_direction = 1  # Towards the right
        else:
            # If no camera, use the old method
            spawn_from_left = random.choice([True, False])
            
            # Use one of the spawn zones for the Y position
            if self.spawn_zones:
                spawn_y = random.choice(self.spawn_zones)
            else:
                spawn_y = self.screen_height // 2 + random.randint(-100, 100)
            
            if spawn_from_left:
                spawn_x = -self.spawn_offset_x
                new_direction = 1
            else:
                spawn_x = self.screen_width + self.spawn_offset_x
                new_direction = -1
        
        # Check that it's not too close to other NPCs
        too_close = False
        new_pos = pygame.math.Vector2(spawn_x, spawn_y)
        
        for other_npc in self.npcs:
            if other_npc != npc:
                other_pos = pygame.math.Vector2(other_npc.rect.centerx, other_npc.rect.centery)
                if new_pos.distance_to(other_pos) < 100:  # Increase the minimum distance to 100px
                    too_close = True
                    break
        
        if too_close:
            # If too close, try a slightly different position
            spawn_x += random.randint(-70, 70)
            spawn_y += random.randint(-70, 70)
        
        # Update position and direction
        npc.rect.center = (spawn_x, spawn_y)
        npc._float_pos = pygame.math.Vector2(npc.rect.x, npc.rect.y)
        npc.direction.x = new_direction
        npc.facing_right = new_direction > 0
        
        # Reset stuck state
        npc.stuck_timer = 0
        npc.last_position = pygame.math.Vector2(npc.rect.center)
        
        # If it was convinced, keep that state
        npc.convinced = current_convinced
        npc.state = current_state
