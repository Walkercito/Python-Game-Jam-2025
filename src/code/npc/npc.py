"""Class representing NPCs with animations and automatic movement."""

import pygame
import os
import random

class NPC(pygame.sprite.Sprite):
    """Handles the logic and animations of NPCs."""

    def __init__(self, pos, animation_paths, speed=120, scale=0.5, direction=None):
        super().__init__()
        self.base_speed = speed
        self.speed = speed
        self.scale = scale
        self.animation_frames = {}
        self.animation_speeds = {'idle': 0.1, 'walking': 0.11}
        self.load_animations(animation_paths)
        self.current_animation = 'walking'
        self.frame_index = 0
        self.animation_timer = 0
        self.direction = pygame.math.Vector2(direction or random.choice([-1, 1]), 0)
        self.facing_right = self.direction.x > 0
        self.state = random.choices(['closed', 'indecisive', 'receptive'], weights=[0.2, 0.5, 0.3])[0]
        
        # Initialize image and rect
        if self.animation_frames.get(self.current_animation):
            self.image = self.animation_frames[self.current_animation][0]['original' if self.facing_right else 'flipped']
        else:
            self.image = pygame.Surface((32, 64))
            self.image.fill(self.get_state_color())
        
        self.rect = self.image.get_rect(center=pos)
        self._float_pos = pygame.math.Vector2(self.rect.topleft)
        self.collision_rect = self.rect.inflate(-10, -10)
        self.setup_interaction_indicator()

    def setup_interaction_indicator(self):
        """Initialize the interaction indicator surface."""
        self.interaction_indicator = pygame.Surface((24, 24), pygame.SRCALPHA)
        self.update_indicator_color()

    def update_indicator_color(self):
        """Update indicator color based on current state."""
        colors = {
            "closed": (255, 50, 50, 200),
            "indecisive": (255, 255, 50, 200),
            "receptive": (50, 255, 50, 200)
        }
        self.interaction_indicator.fill((0, 0, 0, 0))
        pygame.draw.circle(self.interaction_indicator, colors[self.state], (12, 12), 8)

    def get_state_color(self):
        """Return color representation of current state."""
        return {
            "closed": (255, 50, 50),
            "indecisive": (255, 255, 50),
            "receptive": (50, 255, 50)
        }[self.state]

    def load_animations(self, animation_paths):
        """Load animation frames from specified paths."""
        for name, path in animation_paths.items():
            if not os.path.exists(path):
                continue

            frames = []
            try:
                for file in sorted(os.listdir(path)):
                    frame = pygame.image.load(os.path.join(path, file)).convert_alpha()
                    if self.scale != 1.0:
                        frame = pygame.transform.scale(frame, 
                            (int(frame.get_width() * self.scale), 
                            (int(frame.get_height() * self.scale)))
                    frames.append({
                        'original': frame,
                        'flipped': pygame.transform.flip(frame, True, False)
                    })
                
                if frames:
                    self.animation_frames[name] = frames
            except Exception as e:
                print(f"Error loading {name} animations: {str(e)}")

    def animate(self, dt):
        """Progress animation frames based on elapsed time."""
        if not self.animation_frames.get(self.current_animation):
            return

        self.animation_timer += dt
        frame_duration = self.animation_speeds.get(self.current_animation, 0.1)
        
        if self.animation_timer >= frame_duration:
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames[self.current_animation])
            self.animation_timer = 0
            self.update_sprite_image()

    def update_sprite_image(self):
        """Update sprite image based on current frame and direction."""
        frame = self.animation_frames[self.current_animation][self.frame_index]
        self.image = frame['original' if self.facing_right else 'flipped']

    def change_direction(self):
        """Reverse movement direction and flip sprite."""
        self.direction.x *= -1
        self.facing_right = not self.facing_right
        self.update_sprite_image()

    def update(self, dt, screen_width, camera=None, npcs=None):
        """Main update method handling movement and behavior."""
        dt = max(dt, 0.001)
        self.animate(dt)
        
        if self.is_interacting:
            self.handle_interaction(dt)
            return
            
        self.handle_movement(dt, screen_width, camera, npcs)

    def handle_interaction(self, dt):
        """Process interaction state."""
        self.interaction_timer += dt
        if self.interaction_timer >= 2:
            self.is_interacting = False
            self.set_animation('walking')

    def handle_movement(self, dt, screen_width, camera, npcs):
        """Handle NPC movement and collisions."""
        if npcs:
            self.check_collisions(npcs)
            
        self._float_pos.x += self.direction.x * self.speed * dt
        self.rect.x = round(self._float_pos.x)
        self.check_offscreen(screen_width, camera)

    def check_collisions(self, npcs):
        """Detect and resolve collisions with other NPCs."""
        self.collision_rect.center = self.rect.center
        for npc in npcs:
            if npc != self and not npc.is_interacting and self.collision_rect.colliderect(npc.collision_rect):
                self.resolve_collision(npc)
                break

    def resolve_collision(self, other):
        """Resolve collision with another NPC."""
        if random.random() < 0.5:
            self.change_direction()
        else:
            overlap = self.collision_rect.clip(other.collision_rect)
            if overlap.width < overlap.height:
                self._float_pos.x -= overlap.width if self.rect.centerx < other.rect.centerx else overlap.width
            else:
                self._float_pos.y -= overlap.height if self.rect.centery < other.rect.centery else overlap.height
            self.rect.topleft = self._float_pos
        self.collision_cooldown = 0.5

    def check_offscreen(self, screen_width, camera):
        """Handle offscreen behavior and despawning."""
        if camera:
            screen_left = camera.offset.x
            screen_right = screen_left + screen_width
            offscreen = self.rect.right < screen_left - 40 or self.rect.left > screen_right + 40
        else:
            offscreen = self.rect.right < -40 or self.rect.left > screen_width + 40
            
        self.time_offscreen = self.time_offscreen + dt if offscreen else 0
        if self.time_offscreen >= 2.0:
            self.kill()

    def draw_interaction_indicator(self, screen, camera):
        """Draw interaction indicator above NPC."""
        if not self.can_interact:
            return
            
        offset_x = 18 if self.facing_right else -18
        indicator_pos = camera.apply_point((self.rect.centerx + offset_x, self.rect.top - 10))
        screen.blit(self.interaction_indicator, (indicator_pos[0]-12, indicator_pos[1]-12))

class NPCManager:
    """Manages spawning and updating groups of NPCs."""

    def __init__(self, animation_paths, screen_width, screen_height):
        self.animation_paths = animation_paths
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.npcs = pygame.sprite.Group()
        self.spawn_zones = []
        self.update_spawn_zones()

    def update_spawn_zones(self):
        """Calculate vertical spawn zones across screen height."""
        zone_height = 100
        num_zones = max(1, self.screen_height // zone_height)
        self.spawn_zones = [(i * zone_height) + (zone_height // 2) for i in range(num_zones)]

    def spawn_npc(self, camera=None):
        """Spawn new NPC at screen edge with random direction."""
        if len(self.npcs) >= 23:
            return

        direction = random.choice([-1, 1])
        if camera:
            spawn_x = camera.offset.x + (self.screen_width // 2) + (direction * (self.screen_width // 2 + 20))
        else:
            spawn_x = -20 if direction == 1 else self.screen_width + 20

        y_pos = random.choice(self.spawn_zones) + random.randint(-30, 30)
        new_npc = NPC((spawn_x, y_pos), self.animation_paths, direction=direction)
        self.npcs.add(new_npc)

    def update(self, dt, player_rect, camera=None):
        """Main update loop for all NPCs."""
        if len(self.npcs) < 23 and getattr(self, 'spawn_timer', 0) >= 1.0:
            self.spawn_npc(camera)
            self.spawn_timer = 0
        else:
            self.spawn_timer = getattr(self, 'spawn_timer', 0) + dt

        self.update_npc_states(player_rect, camera)

    def update_npc_states(self, player_rect, camera):
        """Update interaction states for all NPCs."""
        interaction_active = any(npc.is_interacting for npc in self.npcs)
        
        for npc in self.npcs:
            npc.update(dt, self.screen_width, camera, self.npcs)
            npc.can_interact = not interaction_active and player_rect.colliderect(npc.rect.inflate(40, 40))

    def draw(self, screen, camera):
        """Draw all NPCs and their indicators."""
        for npc in self.npcs:
            screen.blit(npc.image, camera.apply(npc))
            npc.draw_interaction_indicator(screen, camera)