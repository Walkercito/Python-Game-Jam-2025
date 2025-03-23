import pygame
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, pos, animation_paths, speed=5, scale=1.0):
        super().__init__()
        self.speed = speed
        self.scale = scale  
        self.animation_frames = {}
        self.load_animations(animation_paths)
        self.current_animation = 'idle'
        self.frame_index = 0
        self.image = self.animation_frames[self.current_animation][self.frame_index]['original']
        self.rect = self.image.get_rect(center=pos)
        self.animation_speed = 0.08
        self.direction = pygame.math.Vector2(0, 0)
        self.animation_timer = 0.0
        self.facing_right = True


    def load_animations(self, animation_paths):
        for animation_name, path in animation_paths.items():
            frames = []
            for frame_name in sorted(os.listdir(path)):
                frame_path = os.path.join(path, frame_name)
                # Convertir y escalar de una vez
                frame_image = pygame.image.load(frame_path).convert_alpha()
                if self.scale != 1.0:
                    frame_image = self.scale_image(frame_image)
                frames.append({
                    'original': frame_image,
                    'flipped': pygame.transform.flip(frame_image, True, False)
                })
            self.animation_frames[animation_name] = frames


    def scale_image(self, image):
        new_width = int(image.get_width() * self.scale)
        new_height = int(image.get_height() * self.scale)
        return pygame.transform.scale(image, (new_width, new_height)).convert_alpha()


    def animate(self, dt):
        self.animation_timer += dt
        while self.animation_timer >= self.animation_speed:
            self.animation_timer -= self.animation_speed
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames[self.current_animation])
            if self.facing_right:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['original']
            else:
                self.image = self.animation_frames[self.current_animation][self.frame_index]['flipped']


    def update(self, dt):
        self.animate(dt)
        self.rect.center += self.direction * self.speed * dt


    def set_animation(self, animation_name):
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.frame_index = 0
            self.animation_timer = 0.0


    def move(self, direction):
        self.direction = direction
        if direction.length() > 0:
            self.set_animation('walking')
            # Actualizar dirección
            if direction.x > 0:
                self.facing_right = True
            elif direction.x < 0:
                self.facing_right = False
        else:
            if self.current_animation != 'idle':
                self.set_animation('idle')


    def attack(self):
        self.set_animation('attack')