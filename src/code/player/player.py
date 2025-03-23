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
        self.image = self.animation_frames[self.current_animation][self.frame_index]
        self.rect = self.image.get_rect(center=pos)
        self.animation_speed = 0.15
        self.direction = pygame.math.Vector2(0, 0)
        self.last_update = pygame.time.get_ticks()
        self.facing_right = True


    def load_animations(self, animation_paths):
        for animation_name, path in animation_paths.items():
            frames = []
            for frame_name in sorted(os.listdir(path)):
                frame_path = os.path.join(path, frame_name)
                frame_image = pygame.image.load(frame_path).convert_alpha()

                if self.scale != 1.0:
                    frame_image = self.scale_image(frame_image)
                frames.append(frame_image)
            self.animation_frames[animation_name] = frames


    def scale_image(self, image):
        """Escala una imagen según el factor de escala."""
        new_width = int(image.get_width() * self.scale)
        new_height = int(image.get_height() * self.scale)
        return pygame.transform.scale(image, (new_width, new_height))


    def animate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 1000 * self.animation_speed:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.animation_frames[self.current_animation])
            self.image = self.animation_frames[self.current_animation][self.frame_index]

            if not self.facing_right:
                self.image = pygame.transform.flip(self.image, True, False)


    def update(self):
        self.animate()
        self.rect.center += self.direction * self.speed


    def set_animation(self, animation_name):
        if self.current_animation != animation_name:
            self.current_animation = animation_name
            self.frame_index = 0


    def move(self, direction):
        self.direction = direction
        if direction.length() > 0:
            self.set_animation('walking')
            if direction.x > 0: 
                self.facing_right = True
            elif direction.x < 0: 
                self.facing_right = False
        else:
            self.set_animation('idle')


    def attack(self):
        self.set_animation('attack')