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
        
        self.rect = pygame.Rect(pos[0], pos[1], 32, 64)
        self._float_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        self.direction = pygame.math.Vector2(direction, 0)
        self.facing_right = direction > 0
        self.speed = speed  
        self.new_scale = scale
        
        # Interaction variables
        self.is_interacting = False
        self.can_interact = False
        self.interaction_timer = 0
        self.interaction_duration = 5.0
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
        self.direction_change_chance = 0.001  # Probability of changing direction randomly
        
        # Simplified anti-blocking system
        self.stuck_timer = 0
        self.stuck_threshold = 8.0  # Time threshold to determine if NPC is stuck
        self.last_position = pygame.math.Vector2(pos)
        self.movement_threshold = 10  # Minimum distance to consider real movement
        
        # Internal conviction state
        self.current_indecisive_rate = 0.3
        self.current_closed_rate = 0.3
        
        # For off-screen tracking
        self.time_offscreen = 0
        self.offscreen_limit = 2.0
        self.interaction_indicator = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.load_animations()
        
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
                    
                    if animation_name == "walking" and not self.animations.get("walking"):
                        self.rect.width = frames[0].get_width()
                        self.rect.height = frames[0].get_height()
                        
                    if self.debug:
                        print(f"Loaded {len(frames)} frames for {animation_name}")
                else:
                    print(f"Warning: No frames loaded for animation: {animation_name}")
                    
            except Exception as e:
                print(f"Error processing animation {animation_name}: {e}")
        
        if not self.animations:
            placeholder = pygame.Surface((32, 64))
            placeholder.fill(self.get_color_by_state())
            self.animations['walking'] = [placeholder]
            print("Warning: No animations loaded for NPC. Using placeholder.")
        
        if self.animations.get("walking"):
            first_frame = self.animations["walking"][0]
            self.rect.width = first_frame.get_width()
            self.rect.height = first_frame.get_height()

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
            
            if self.animation_sequence:
                animation_frames = self.animations[self.current_animation]
                self.animation_index = (self.animation_index + 1) % len(animation_frames)
                
                if self.animation_index == 0:
                    self.animation_played = True
                    
                    self.current_sequence_index += 1

                    if self.current_sequence_index < len(self.animation_sequence):
                        self.current_animation = self.animation_sequence[self.current_sequence_index]
                        self.animation_index = 0
                    else:
                        self.animation_sequence = []
                        self.current_sequence_index = 0
                        
                        if self.convinced:
                            self.current_animation = "convinced_walking"
                        else:
                            self.current_animation = "walking"
                        
                        # Allow movement immediately after sequence ends
                        self.is_interacting = False
                        self.interaction_timer = 0
            else:
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

        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
            
        if self.direction_change_cooldown > 0:
            self.direction_change_cooldown -= dt
            if self.direction_change_cooldown <= 0:
                self.can_change_direction = True
        
        if self.is_interacting:
            self.interaction_timer += dt
            if self.interaction_timer >= self.interaction_duration:
                self.is_interacting = False
                self.interaction_timer = 0
                
                if not self.animation_sequence:
                    self.set_animation('walking')
                
                self.animation_played = False
            retur
        current_pos = pygame.math.Vector2(self.rect.center)
        distance_moved = current_pos.distance_to(self.last_position)
        
        if distance_moved < self.movement_threshold:
            self.stuck_timer += dt
            if self.stuck_timer > 8.0: 
                self._float_pos.x += self.direction.x * 20 
                self.rect.x = round(self._float_pos.x)
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
            self.last_position = current_pos
        
        if self.can_change_direction and random.random() < 0.001: 
            self.change_direction()
            self.can_change_direction = False
            self.direction_change_cooldown = 3.0
        
        # Check for collisions with other NPCs - only if the cooldown has expired
        if other_npcs and self.collision_cooldown <= 0:
            self.check_collision(other_npcs)

        if self.direction.length() > 0:
            move_x = self.direction.x * self.speed * dt
            
            # If the NPC has been convinced, make sure it heads out of the screen
            if self.convinced:
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
                screen_left = camera.offset.x
                screen_right = camera.offset.x + screen_width

                if (self.rect.right < screen_left - 40) or (self.rect.left > screen_right + 40):
                    is_offscreen = True
            else:
                if self.rect.right < -40 or self.rect.left > screen_width + 40:
                    is_offscreen = True
            
            if is_offscreen:
                if self.convinced:
                    self.time_offscreen += dt
                    if self.time_offscreen >= self.offscreen_limit:
                        self.kill() 
                else:
                    self.change_direction()
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
                
                if self.collision_rect.colliderect(npc.collision_rect):
                    my_pos = pygame.math.Vector2(self.rect.center)
                    other_pos = pygame.math.Vector2(npc.rect.center)
                    
                    separation = my_pos - other_pos
                    if separation.length() > 0:
                        separation.normalize_ip()
                        self._float_pos.x += separation.x * 10
                        self._float_pos.y += separation.y * 3
                    
                    self.rect.x = round(self._float_pos.x)
                    self.rect.y = round(self._float_pos.y)
                    
                    self.collision_cooldown = 0.5
                    collision_occurred = True
        
        return collision_occurred

    def interact(self, player=None):
        """Handle player interaction with this NPC.
        
        Returns:
            True if interaction was successful, False otherwise.
        """
        if self.is_interacting or hasattr(self, '_processing_interaction') and self._processing_interaction:
            return False
            
        if player:
            conviction_rate = 0.5
            if hasattr(player, 'get_conviction_rate'):
                conviction_rate = player.get_conviction_rate()
            
            self.is_interacting = True
            self._processing_interaction = True 
            
            # Prepare animation sequence
            new_animation_sequence = ['book']
            was_convinced = False
            became_more_receptive = False
            became_more_closed = False
            
            # Change behavior based on current state
            if self.state == "CLOSED":
                convinced = random.random() < (conviction_rate * 0.3)
                became_more_receptive = random.random() < (conviction_rate * 0.4)
                
                if convinced:
                    self.convinced = True
                    was_convinced = True
                    new_animation_sequence.append('convinced')
                    
                    # Increase player influence (success)
                    if hasattr(player, 'update_influence'):
                        player.update_influence(10.0)
                    
                    # Recover energy on success
                    if hasattr(player, 'update_energy'):
                        player.update_energy(-5.0)
                elif became_more_receptive:
                    self.state = "INDECISIVE"
                    new_animation_sequence.append('indecisive')
                    
                    # Increase a bit of influence (partial progress)
                    if hasattr(player, 'update_influence'):
                        player.update_influence(3.0)
                    if hasattr(player, 'update_energy'):
                        player.update_energy(4.0)
                else:
                    new_animation_sequence.append('closed')
                    if hasattr(player, 'update_energy'):
                        player.update_energy(6.0)
                    
            elif self.state == "INDECISIVE":
                convinced = random.random() < (conviction_rate * 0.6)
                became_more_closed = random.random() < (1 - conviction_rate * 0.7)
                
                if convinced:
                    self.convinced = True
                    was_convinced = True
                    new_animation_sequence.append('convinced')

                    if hasattr(player, 'update_influence'):
                        player.update_influence(7.0)

                    if hasattr(player, 'update_energy'):
                        player.update_energy(-4.0)
                elif became_more_closed:
                    self.state = "CLOSED"
                    new_animation_sequence.append('closed')

                    if hasattr(player, 'update_influence'):
                        player.update_influence(-2.0)

                    if hasattr(player, 'update_energy'):
                        player.update_energy(5.0)
                else:
                    new_animation_sequence.append('indecisive')
                    
                    if hasattr(player, 'update_energy'):
                        player.update_energy(3.5)
                    
            elif self.state == "RECEPTIVE":
                convinced = random.random() < (conviction_rate * 0.9)
                became_more_closed = random.random() < (1 - conviction_rate * 0.9)
                
                if convinced:
                    self.convinced = True
                    was_convinced = True
                    new_animation_sequence.append('convinced')

                    if hasattr(player, 'update_influence'):
                        player.update_influence(5.0)

                    if hasattr(player, 'update_energy'):
                        player.update_energy(-3.0)
                elif became_more_closed:
                    self.state = "INDECISIVE"
                    new_animation_sequence.append('indecisive')

                    if hasattr(player, 'update_influence'):
                        player

    def get_player(self):
        """Gets the player instance from the manager. To be implemented by manager."""
        # This is just a placeholder - the actual implementation will be in NPCManager
        return None

    def draw_interaction_indicator(self, screen, camera):
        """Draw an indicator when the player can interact with this NPC."""
        if self.can_interact:
            indicator_pos = camera.apply_point((self.rect.centerx + 5, self.rect.top + 5))
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
            npc.update(dt=dt, screen_width=self.screen_width, camera=camera, other_npcs=self.npcs)
            
            if camera:
                player_center_x = camera.offset.x + (self.screen_width // 2)
                player_center_y = camera.offset.y + (self.screen_height // 2)
                
                left_bound = player_center_x - (self.screen_width // 2) - 150
                right_bound = player_center_x + (self.screen_width // 2) + 150
                top_bound = player_center_y - (self.screen_height // 2) - 150
                bottom_bound = player_center_y + (self.screen_height // 2) + 150

                if (npc.rect.right < left_bound or npc.rect.left > right_bound or 
                    npc.rect.bottom < top_bound or npc.rect.top > bottom_bound):
                    npcs_to_respawn.append(npc)
            else:
                if npc.rect.right < -100 or npc.rect.left > self.screen_width + 100:
                    npcs_to_respawn.append(npc)
        

        for npc in npcs_to_respawn:
            self.respawn_npc(npc, camera)
        
        if was_interaction_active and not self.interaction_active and self.player:
            if hasattr(self.player, 'update_gameplay_stats'):
                self.player.update_gameplay_stats(dt, rejected=False)
                    
    def handle_interaction(self, player_rect, keys):
        """Handle player interaction with NPCs."""
        if self.interaction_active:
            return False

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
        
        for npc in self.npcs:
            npc.can_interact = (npc == nearest_npc)
        
        # Check if player pressed the interaction key
        interacted = False
        if nearest_npc and keys[pygame.K_e]:
            if self.player:
                self.player.attack()
            
            if nearest_npc.interact(self.player):
                self.interaction_active = True
                interacted = True
        
        return interacted
    
    def draw(self, screen, camera):
        """Draw all NPCs and their interaction indicators."""
        npcs_to_draw = sorted(self.npcs.sprites(), key=lambda npc: npc.rect.bottom)
        
        for npc in npcs_to_draw:
            npc_rect = camera.apply(npc.rect)
            screen.blit(npc.image, npc_rect)
            
            npc.draw_interaction_indicator(screen, camera)

    def spawn_npc(self, camera=None):
        """Spawn a new NPC at the right or left edge of the screen."""
        if len(self.npcs) >= self.max_npcs:
            return
            
        npc = NPC(
            pos = (0, 0),
            animation_paths = self.animation_paths,
            speed = 120,
            scale = 0.5,
            direction = 1
        )
        
        if self.player:
            npc.get_player = lambda: self.player
        else:
            npc.get_player = lambda: None

        current_convinced = npc.convinced
        current_state = npc.state
        
        if camera:
            player_center_x = camera.offset.x + (self.screen_width // 2)
            player_center_y = camera.offset.y + (self.screen_height // 2)
            
            spawn_side = random.choice([1, 3])
            if spawn_side == 1: 
                spawn_x = player_center_x + (self.screen_width // 2) + self.spawn_offset_x
                spawn_y = player_center_y + random.randint(-self.screen_height//3, self.screen_height//3)
                new_direction = -1 
            else:
                spawn_x = player_center_x - (self.screen_width // 2) - self.spawn_offset_x
                spawn_y = player_center_y + random.randint(-self.screen_height//3, self.screen_height//3)
                new_direction = 1 
        else:
            spawn_from_left = random.choice([True, False])

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

        too_close = False
        new_pos = pygame.math.Vector2(spawn_x, spawn_y)
        
        for other_npc in self.npcs:
            if other_npc != npc:
                other_pos = pygame.math.Vector2(other_npc.rect.centerx, other_npc.rect.centery)
                if new_pos.distance_to(other_pos) < 100:  # Increase the minimum distance to 100px
                    too_close = True
                    break
        
        if too_close:
            spawn_x += random.randint(-70, 70)
            spawn_y += random.randint(-70, 70)
        
        npc.rect.center = (spawn_x, spawn_y)
        npc._float_pos = pygame.math.Vector2(npc.rect.x, npc.rect.y)
        npc.direction.x = new_direction
        npc.facing_right = new_direction > 0
        
        npc.stuck_timer = 0
        npc.last_position = pygame.math.Vector2(npc.rect.center)
        
        npc.convinced = current_convinced
        npc.state = current_state

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
            

            spawn_side = random.choice([1, 3])
            
            if spawn_side == 1: 
                spawn_x = player_center_x + (self.screen_width // 2) + self.spawn_offset_x
                spawn_y = player_center_y + random.randint(-self.screen_height//3, self.screen_height//3)
                new_direction = -1
            else:  
                spawn_x = player_center_x - (self.screen_width // 2) - self.spawn_offset_x
                spawn_y = player_center_y + random.randint(-self.screen_height//3, self.screen_height//3)
                new_direction = 1
        else:
            spawn_from_left = random.choice([True, False])

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
            spawn_x += random.randint(-70, 70)
            spawn_y += random.randint(-70, 70)

        npc.rect.center = (spawn_x, spawn_y)
        npc._float_pos = pygame.math.Vector2(npc.rect.x, npc.rect.y)
        npc.direction.x = new_direction
        npc.facing_right = new_direction > 0
        
        npc.stuck_timer = 0
        npc.last_position = pygame.math.Vector2(npc.rect.center)

        npc.convinced = current_convinced
        npc.state = current_state
