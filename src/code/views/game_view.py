import pygame
#from utils import draw_fps
from src.code.player.player import Player
from constants import width, height, gray


class GameView:
    def __init__(self, switch_view, animation_paths):
        self.switch_view = switch_view
        self.design_width = width
        self.design_height = height

        self.player = Player(
            pos = (width // 2, height // 2), 
            animation_paths=animation_paths,
            speed = 5,
            scale = 0.5
        )


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.switch_view("main")

        keys = pygame.key.get_pressed()
        direction = pygame.math.Vector2(0, 0)
        
        if keys[pygame.K_w]:
            direction.y = -1
        if keys[pygame.K_s]:
            direction.y = 1
        if keys[pygame.K_a]:
            direction.x = -1
        if keys[pygame.K_d]:
            direction.x = 1
        
        if direction.length() > 0:
            direction.normalize_ip()
        
        self.player.move(direction)


    def update(self):
        self.player.update()


    def draw(self, screen):
        screen.fill(gray)
        #draw_fps(screen, clock, font, screen.get_width())
        screen.blit(self.player.image, self.player.rect)


    def handle_resize(self, new_width, new_height):
        scale_x = new_width / self.design_width
        scale_y = new_height / self.design_height


