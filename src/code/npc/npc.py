"""Class representing NPCs with animations and automatic movement."""

import pygame
import os
import random


class NPC(pygame.sprite.Sprite):
    """Handles the logic and animations of NPCs."""

    def __init__(self, pos, animation_paths, speed = 150, scale=0.5, direction=None):
        """Initializes the NPC with position and animations."""
        super().__init__()
        self.base_speed = speed
        self.speed = speed
        self.scale = scale
        self.animation_frames = {}
        self.animation_speeds = {
            'idle': 0.125,
            'walking': 0.125,
        }
        self.debug = False
        self.load_animations(animation_paths)
        self.current_animation = 'walking'
        self.frame_index = 0
        self.animation_timer = 0
        
        if direction is None:
            direction = random.choice([-1, 1])
        self.direction = pygame.math.Vector2(direction, 0)
        self.facing_right = direction > 0
        
        self.can_change_direction = True
        self.direction_change_cooldown = 0
        self.direction_change_chance = 0.005
        
        self.time_offscreen = 0
        self.offscreen_limit = 2.0
        
        self.state = self.assign_initial_state()
        self.interaction_timer = 0
        self.is_interacting = False
        self.interaction_duration = 2
        
        if self.current_animation in self.animation_frames and len(self.animation_frames[self.current_animation]) > 0:
            self.image = self.animation_frames[self.current_animation][0]['original' if self.facing_right else 'flipped']
        else:
            # Create a fallback image if animations aren't loaded - make it bigger
            self.image = pygame.Surface((32, 64))
            self.image.fill(self.get_color_by_state())
            
        self.rect = self.image.get_rect(center=pos)
        
        self._float_pos = pygame.math.Vector2(self.rect.x, self.rect.y)
        
        # Interaction indicator
        self.can_interact = False
        self.interaction_indicator = pygame.Surface((16, 16), pygame.SRCALPHA)
        self.update_interaction_indicator()
        
        # Collision avoidance
        self.collision_rect = self.rect.inflate(-10, -10)
        self.collision_cooldown = 0

    def update_interaction_indicator(self):
        """Update the interaction indicator color based on NPC state."""
        self.interaction_indicator = pygame.Surface((24, 24), pygame.SRCALPHA)
        
        if self.state == "closed":
            color = (255, 50, 50, 200)  # Red for closed
        elif self.state == "indecisive":
            color = (255, 255, 50, 200)  # Yellow for indecisive
        else:
            color = (50, 255, 50, 200)  # Green for receptive
            
        pygame.draw.circle(self.interaction_indicator, color, (12 if self.facing_right else 12, 12), 8)

    def assign_initial_state(self):
        """Assigns an initial state to the NPC based on probabilities."""
        # For now, simple random assignment
        # 20% chance of being closed, 50% indecisive, 30% receptive
        roll = random.random()
        if roll < 0.2:
            return "closed"
        elif roll < 0.7:
            return "indecisive"
        else:
            return "receptive"

    def get_color_by_state(self):
        """Returns a color based on the NPC's state."""
        if self.state == "closed":
            return (255, 50, 50)  # Brighter red for closed
        elif self.state == "indecisive":
            return (255, 255, 50)  # Brighter yellow for indecisive
        else:
            return (50, 255, 50)   # Brighter green for receptive

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
                else:
                    print(f"Warning: No frames loaded for animation: {animation_name}")
                    
            except Exception as e:
                print(f"Error processing animation {animation_name}: {e}")
        
        # Create a placeholder if no animations were loaded
        if not self.animation_frames:
            placeholder = pygame.Surface((32, 64))
            placeholder.fill(self.get_color_by_state())
            flipped = placeholder.copy()
            self.animation_frames['idle'] = [{'original': placeholder, 'flipped': flipped}]
            self.animation_frames['walking'] = [{'original': placeholder, 'flipped': flipped}]
            print("Warning: No animations loaded for NPC. Using placeholder.")
            
        for anim_name in self.animation_frames:
            if anim_name not in self.animation_speeds:
                self.animation_speeds[anim_name] = 0.1  # Default speed

    def get_current_animation_speed(self):
        """Returns the speed for the current animation."""
        return self.animation_speeds.get(self.current_animation, 0.1)  # Default to 0.1 if not found

    def animate(self, dt):
        """Updates the NPC's animation frame."""
        # Check if animation exists
        if self.current_animation not in self.animation_frames:
            if self.debug:
                print(f"Animation '{self.current_animation}' not found!")
            return
            
        current_speed = self.get_current_animation_speed()
            
        self.animation_timer += dt
        frames_count = len(self.animation_frames[self.current_animation])
        
        if self.animation_timer >= current_speed:
            while self.animation_timer >= current_speed:
                self.animation_timer -= current_speed
                self.frame_index = (self.frame_index + 1) % frames_count
                
            # Update the image based on direction
            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['original']
            else:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['flipped']

    def change_direction(self):
        """Changes the NPC's direction."""
        self.direction.x *= -1
        self.facing_right = not self.facing_right

        if self.current_animation in self.animation_frames and len(self.animation_frames[self.current_animation]) > 0:
            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['original']
            else:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['flipped']

    def check_collision(self, other_npcs):
        """Checks and handles collisions with other NPCs."""
        if self.collision_cooldown > 0:
            return False
            
        self.collision_rect.center = self.rect.center
        
        for npc in other_npcs:
            if npc != self and not npc.is_interacting:
                npc.collision_rect.center = npc.rect.center
                
                # Check for collision
                if self.collision_rect.colliderect(npc.collision_rect):
                    if random.random() < 0.5:
                        self.change_direction()
                    else:
                        overlap = self.collision_rect.clip(npc.collision_rect)
                        if overlap.width < overlap.height:
                            if self.rect.centerx < npc.rect.centerx:
                                self._float_pos.x -= overlap.width
                            else:
                                self._float_pos.x += overlap.width
                        else:
                            if self.rect.centery < npc.rect.centery:
                                self._float_pos.y -= overlap.height
                            else:
                                self._float_pos.y += overlap.height
                                
                    # Update the position of the rectangle
                    self.rect.x = round(self._float_pos.x)
                    self.rect.y = round(self._float_pos.y)
                    
                    # Set cooldown to avoid multiple collisions in a row
                    self.collision_cooldown = 0.5
                    return True
        
        return False

    def update(self, dt, screen_width, camera=None, other_npcs=None):
        """Updates the NPC's position and animation."""
        dt = max(dt, 0.001)
        self.animate(dt)
        
        if self.collision_cooldown > 0:
            self.collision_cooldown -= dt
        
        if self.is_interacting:
            self.interaction_timer += dt
            if self.interaction_timer >= self.interaction_duration:
                self.is_interacting = False
                self.interaction_timer = 0
                self.set_animation('walking')
            return  # Don't move while interacting
        
        if self.direction_change_cooldown > 0:
            self.direction_change_cooldown -= dt
            if self.direction_change_cooldown <= 0:
                self.can_change_direction = True
        
        if self.can_change_direction and random.random() < self.direction_change_chance:
            self.change_direction()
            self.can_change_direction = False
            self.direction_change_cooldown = 1.0  
        
        # Check for collisions with other NPCs
        if other_npcs:
            self.check_collision(other_npcs)
        
        if self.direction.length() > 0:
            move_x = self.direction.x * self.speed * dt
            
            self._float_pos.x += move_x
            self.rect.x = round(self._float_pos.x)
            is_offscreen = False
            
            if camera:
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
                self.time_offscreen += dt
                if self.time_offscreen >= self.offscreen_limit:
                    self.kill()  # Remove NPC if off-screen for too long
            else:
                self.time_offscreen = 0 

    def set_animation(self, animation_name):
        """Changes the NPC's current animation."""
        if (animation_name in self.animation_frames and 
            self.current_animation != animation_name):
            
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_timer = 0

            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][0]['original']
            else:
                self.image = self.animation_frames[self.current_animation][0]['flipped']

    def interact(self):
        """Handle player interaction with the NPC."""
        if not self.is_interacting:
            self.is_interacting = True
            self.interaction_timer = 0
            self.set_animation('idle')
            
            if self.state == "closed":
                print(f"Closed NPC rejects the interaction")
            elif self.state == "indecisive":
                print(f"Indecisive NPC hesitates about the interaction")
            elif self.state == "receptive":
                print(f"Receptive NPC accepts the interaction")
            
            return True
        return False

    def draw_interaction_indicator(self, screen, camera):
        """Draw an indicator when the player can interact with this NPC."""
        if self.can_interact:
            offset_x = 18 if self.facing_right else -18
            indicator_pos = camera.apply_point((self.rect.centerx + offset_x, self.rect.top - 10))
            screen.blit(self.interaction_indicator, (indicator_pos[0] - 12, indicator_pos[1] - 12))


class NPCManager:
    """Manages the spawning and updating of NPCs."""
    
    def __init__(self, animation_paths, screen_width, screen_height):
        """Initialize the NPC manager."""
        self.animation_paths = animation_paths
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.npcs = pygame.sprite.Group()
        self.spawn_timer = 0
        self.spawn_interval = 1.0
        
        self.max_npcs = 23
        
        self.spawn_offset_x = 20
        
        self.interaction_active = False
        
        self.spawn_zones = []
        self.update_spawn_zones()
        
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
        
        self.interaction_active = False
        for npc in self.npcs:
            if npc.is_interacting:
                self.interaction_active = True
                break
        
        for npc in self.npcs:
            npc.update(dt, self.screen_width, camera, self.npcs)
            
            if not self.interaction_active:
                npc.can_interact = player_rect.colliderect(npc.rect.inflate(40, 40))
            else:
                npc.can_interact = False
    
    def spawn_npc(self, camera=None):
        """Spawn a new NPC at the right or left edge of the screen."""
        if len(self.npcs) >= self.max_npcs:
            return
            
        spawn_from_left = random.choice([True, False])
        
        if camera:
            player_center_x = camera.offset.x + (self.screen_width // 2)
            
            if spawn_from_left:
                spawn_x = player_center_x - (self.screen_width // 2) - self.spawn_offset_x
                direction = 1
            else:
                spawn_x = player_center_x + (self.screen_width // 2) + self.spawn_offset_x
                direction = -1
        else:
            if spawn_from_left:
                spawn_x = -self.spawn_offset_x
                direction = 1
            else:
                spawn_x = self.screen_width + self.spawn_offset_x
                direction = -1
            
        if not self.spawn_zones:
            self.update_spawn_zones()
            
        if self.spawn_zones:
            base_y = random.choice(self.spawn_zones)
            y_variation = random.randint(-30, 30)
            y_pos = base_y + y_variation
        else:
            y_pos = self.screen_height // 2 + random.randint(-100, 100)
        
        too_close = False
        new_pos = pygame.math.Vector2(spawn_x, y_pos)
        
        for npc in self.npcs:
            npc_pos = pygame.math.Vector2(npc.rect.centerx, npc.rect.centery)
            if new_pos.distance_to(npc_pos) < 100:
                too_close = True
                break
                
        if too_close:
            return
        
        npc = NPC(
            pos=(spawn_x, y_pos),
            animation_paths=self.animation_paths,
            speed=120,
            scale=0.5,
            direction=direction
        )
        
        self.npcs.add(npc)
    
    def handle_interaction(self, player_rect, keys):
        """Handle player interaction with NPCs."""
        if self.interaction_active:
            return False
            
        for npc in self.npcs:
            if npc.can_interact and keys[pygame.K_e]:
                if npc.interact():
                    self.interaction_active = True
                    return True
        return False
    
    def draw(self, screen, camera):
        """Draw all NPCs and their interaction indicators."""
        for npc in self.npcs:
            npc_rect = camera.apply(npc)
            screen.blit(npc.image, npc_rect)
            
            npc.draw_interaction_indicator(screen, camera)
