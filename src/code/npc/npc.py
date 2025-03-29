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
                            self.current_animation = "convinced_walking"
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
        """Handle player interaction with this NPC.
        
        Returns:
            True if interaction was successful, False otherwise.
        """
        if self.is_interacting:
            return False
            
        if player:
            # Get player's conviction rate (between 0.0 and 1.0)
            conviction_rate = 0.5  # Default value
            if hasattr(player, 'get_conviction_rate'):
                conviction_rate = player.get_conviction_rate()
            
            # Start interaction
            self.is_interacting = True
            
            # Initial state to determine if NPC was convinced
            was_convinced = False
            became_more_receptive = False
            became_more_closed = False
            
            # Change behavior based on current state
            if self.state == "CLOSED":
                convinced = random.random() < (conviction_rate * 0.3)
                # Determine if NPC became more receptive
                became_more_receptive = random.random() < (conviction_rate * 0.4)
                
                if convinced:
                    # NPC was convinced
                    self.convinced = True
                    was_convinced = True
                    # Sequence: book -> convinced -> walking (to exit)
                    self.set_animation_sequence(['book', 'convinced'])
                    
                    # Increase player influence (success)
                    if hasattr(player, 'update_influence'):
                        player.update_influence(10.0)  # Bonus for convincing a closed NPC
                    
                    # Recover energy on success
                    if hasattr(player, 'update_energy'):
                        player.update_energy(-5.0)  # Negative value to recover energy
                elif became_more_receptive:
                    # NPC became more receptive (moves to indecisive)
                    self.state = "INDECISIVE"
                    # Sequence: book -> indecisive -> walking
                    self.set_animation_sequence(['book', 'indecisive'])
                    
                    # Increase a bit of influence (partial progress)
                    if hasattr(player, 'update_influence'):
                        player.update_influence(3.0)
                    
                    # Consume less energy
                    if hasattr(player, 'update_energy'):
                        player.update_energy(4.0)
                else:
                    # NPC remains closed
                    # Sequence: book -> closed -> walking
                    self.set_animation_sequence(['book', 'closed'])
                    
                    # No influence increase (failure)
                    # Consume less energy for rejection
                    if hasattr(player, 'update_energy'):
                        player.update_energy(6.0)  # Lower energy cost
                
            elif self.state == "INDECISIVE":
                convinced = random.random() < (conviction_rate * 0.6)
                # Determine if NPC became more closed
                became_more_closed = random.random() < (1 - conviction_rate * 0.7)
                
                if convinced:
                    # NPC was convinced
                    self.convinced = True
                    was_convinced = True
                    # Sequence: book -> convinced -> walking (to exit)
                    self.set_animation_sequence(['book', 'convinced'])
                    
                    # Increase player influence
                    if hasattr(player, 'update_influence'):
                        player.update_influence(7.0)  # Bonus for convincing an indecisive NPC
                    
                    # Recover energy on success
                    if hasattr(player, 'update_energy'):
                        player.update_energy(-4.0)  # Negative value to recover energy
                elif became_more_closed:
                    # NPC became more closed
                    self.state = "CLOSED"
                    # Sequence: book -> closed -> walking
                    self.set_animation_sequence(['book', 'closed'])
                    
                    # Lose a bit of influence for setback
                    if hasattr(player, 'update_influence'):
                        player.update_influence(-2.0)  # Loss for setback
                    
                    # Consume less energy
                    if hasattr(player, 'update_energy'):
                        player.update_energy(5.0)
                else:
                    # NPC still indecisive
                    # Sequence: book -> indecisive -> walking
                    self.set_animation_sequence(['book', 'indecisive'])
                    
                    # Neither increase nor decrease influence
                    # Consume normal energy
                    if hasattr(player, 'update_energy'):
                        player.update_energy(3.5)
                
            elif self.state == "RECEPTIVE":
                convinced = random.random() < (conviction_rate * 0.9)
                # Determine if NPC became more closed
                became_more_closed = random.random() < (1 - conviction_rate * 0.9)
                
                if convinced:
                    # NPC was convinced
                    self.convinced = True
                    was_convinced = True
                    # Sequence: book -> convinced -> walking (to exit)
                    self.set_animation_sequence(['book', 'convinced'])
                    
                    # Increase player influence
                    if hasattr(player, 'update_influence'):
                        player.update_influence(5.0)  # Bonus for convincing a receptive NPC
                    
                    # Recover energy on success
                    if hasattr(player, 'update_energy'):
                        player.update_energy(-3.0)  # Negative value to recover energy
                elif became_more_closed:
                    # NPC became more closed
                    self.state = "INDECISIVE"
                    # Sequence: book -> indecisive -> walking
                    self.set_animation_sequence(['book', 'indecisive'])
                    
                    # Lose a bit of influence for setback
                    if hasattr(player, 'update_influence'):
                        player.update_influence(-1.0)
                    
                    # Consume normal energy
                    if hasattr(player, 'update_energy'):
                        player.update_energy(3.0)
                else:
                    # No change in attitude but not convinced
                    # Sequence: book -> indecisive -> walking (using indecisive as fallback)
                    self.set_animation_sequence(['book', 'indecisive'])
                    
                    # Neither increase nor decrease influence
                    # Consume normal energy
                    if hasattr(player, 'update_energy'):
                        player.update_energy(2.5)
            
            # Visual and sound feedback based on result
            self.update_interaction_indicator()  # Update indicator color based on new state
            
            return True
        
        return False

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
        
        self.spawn_offset_x = 100  # Increased from 20 to 100 to make them appear farther
        
        self.interaction_active = False
        
        self.spawn_zones = []
        self.update_spawn_zones()
        
        self.player = player  # Store the player instance
        
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
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval and len(self.npcs) < self.max_npcs:
            self.spawn_timer = 0
            self.spawn_npc(camera)
        
        # Check if any NPC is interacting
        was_interaction_active = self.interaction_active
        self.interaction_active = False
        for npc in self.npcs:
            if npc.is_interacting:
                self.interaction_active = True
                break
        
        # List of NPCs to respawn
        npcs_to_respawn = []
        
        for npc in self.npcs:
            # REMOVE COLLISION CHECK HERE to avoid continuous changes
            # self.check_npc_collision(npc)
            
            # Call the original update method of the NPC
            npc.update(dt=dt, screen_width=self.screen_width, camera=camera, other_npcs=self.npcs)
            
            # The interaction state is now updated in handle_interaction
            # to show only the closest NPC
                
            # Check if the NPC is off-screen and needs to respawn
            if camera:
                player_center_x = camera.offset.x + (self.screen_width // 2)
                player_center_y = camera.offset.y + (self.screen_height // 2)
                
                # Wider limits to respawn
                left_bound = player_center_x - (self.screen_width // 2) - 150
                right_bound = player_center_x + (self.screen_width // 2) + 150
                top_bound = player_center_y - (self.screen_height // 2) - 150
                bottom_bound = player_center_y + (self.screen_height // 2) + 150
                
                # If off-screen, add to the list to respawn
                if (npc.rect.right < left_bound or npc.rect.left > right_bound or 
                    npc.rect.bottom < top_bound or npc.rect.top > bottom_bound):
                    npcs_to_respawn.append(npc)
            else:
                if npc.rect.right < -100 or npc.rect.left > self.screen_width + 100:
                    npcs_to_respawn.append(npc)
        
        # Respawn all off-screen NPCs
        for npc in npcs_to_respawn:
            self.respawn_npc(npc, camera)
        
        # If the player is no longer interacting with any NPC, update statistics
        if was_interaction_active and not self.interaction_active and self.player:
            # Check if the player has the update_gameplay_stats method before calling it
            if hasattr(self.player, 'update_gameplay_stats'):
                self.player.update_gameplay_stats(dt, rejected=False)
                    
    def handle_interaction(self, player_rect, keys):
        """Handle player interaction with NPCs."""
        if self.interaction_active:
            return False
            
        # Check if at least one NPC has can_interact=True
        has_interactable = False
        
        # First pass: find all NPCs that could be interacted with
        can_interact_npcs = []
        for npc in self.npcs:
            if not npc.is_interacting and player_rect.colliderect(npc.rect.inflate(40, 40)):
                can_interact_npcs.append(npc)
                
        # If none found, exit
        if not can_interact_npcs:
            # Make sure no NPC has the indicator shown
            for npc in self.npcs:
                npc.can_interact = False
            return False
            
        # Find the closest NPC to the player
        nearest_npc = None
        min_distance = float('inf')
        player_center = pygame.math.Vector2(player_rect.center)
        
        for npc in can_interact_npcs:
            npc_center = pygame.math.Vector2(npc.rect.center)
            distance = player_center.distance_to(npc_center)
            
            if distance < min_distance:
                min_distance = distance
                nearest_npc = npc
        
        # Now only show the indicator for the nearest NPC
        for npc in self.npcs:
            npc.can_interact = (npc == nearest_npc)
        
        # Check if player pressed the interaction key
        interacted = False
        if nearest_npc and keys[pygame.K_e]:
            # Use the attack method directly instead of set_animation
            if self.player:
                self.player.attack()
            
            if nearest_npc.interact(self.player):
                self.interaction_active = True
                interacted = True
        
        return interacted
    
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
            
        # Create a new NPC with the correct speed
        npc = NPC(
            pos=(0, 0),
            animation_paths=self.animation_paths,
            speed=120,  # Make sure to use the correct speed
            scale=0.5,
            direction=1
        )
        
        # Set the player instance for the NPC
        if self.player:
            npc.get_player = lambda: self.player
        else:
            npc.get_player = lambda: None
        
        # Save current states to keep them after updating the position
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
        
        # Add to the list of NPCs
        self.npcs.add(npc)
        
        return npc

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