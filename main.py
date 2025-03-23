import pygame
import constants as const
from src.code.views.main_menu import MainMenu


class Game:
    def __init__(self):
        pygame.init()

        self.animation_paths = {
        'idle': './src/assets/player/idle',
        'walking': './src/assets/player/walking',
        'attack': './src/assets/player/idle',
    }

        self.design_width = const.width
        self.design_height = const.height

        self.WIDTH = const.width
        self.HEIGHT = const.height
        self.FPS = 60
        self.fullscreen = False
        self.windowed_size = (self.WIDTH, self.HEIGHT)
        
        self.clock = pygame.time.Clock()
        self.font = None  

        self.window = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption(const.title)
        
        self.current_view = None
        self.switch_view("main") 
        self.handle_resize()


    def handle_resize(self):
        """Ajusta elementos al cambiar tamaño de ventana"""
        scale = min(
            self.WIDTH / self.design_width, 
            self.HEIGHT / self.design_height
        )
        self.font = pygame.font.Font(const.font_path, int(const.font_sizes["medium"] * scale))

        if self.current_view:
            self.current_view.handle_resize(self.WIDTH, self.HEIGHT)


    def switch_view(self, view_name):
        """Cambia entre vistas"""
        if view_name == "main":
            self.current_view = MainMenu(
                switch_view=self.switch_view,
                design_width=self.design_width,
                design_height=self.design_height  
            )
        elif view_name == "game":
            from src.code.views.game_view import GameView
            self.current_view = GameView(self.switch_view, self.animation_paths)
        elif view_name == "settings":
            pass
        elif view_name == "exit":
            pygame.quit()
        
        if self.current_view:
            self.current_view.handle_resize(self.WIDTH, self.HEIGHT)


    def update(self):
        """Actualiza la lógica del juego"""
        self.window.fill(const.black)
        
        if self.current_view:
            self.current_view.draw(self.window)


    def run(self):
        running = True

        while running:
            self.clock.tick(self.FPS)
            events = pygame.event.get()

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                    break
                
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.WIDTH, self.HEIGHT = event.w, event.h
                        self.windowed_size = (self.WIDTH, self.HEIGHT)
                        self.handle_resize()
                
                elif event.type == pygame.KEYDOWN:
                    # toggle fullscreen with f14 and f key
                    if event.key in (pygame.K_F11, pygame.K_f):
                        self.fullscreen = not self.fullscreen
                        
                        if self.fullscreen:
                            self.windowed_size = (self.WIDTH, self.HEIGHT)
                            self.window = pygame.display.set_mode(
                                (0, 0), 
                                pygame.FULLSCREEN
                            )
                        else:
                            self.window = pygame.display.set_mode(
                                self.windowed_size, 
                                pygame.RESIZABLE
                            )
                        
                        self.WIDTH, self.HEIGHT = self.window.get_size()
                        self.handle_resize()

                if self.current_view:
                    self.current_view.handle_events(events)
                    if hasattr(self.current_view, "update"):
                        self.current_view.update()
            
            if not running:
                break

            self.update()
            pygame.display.flip()
        
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()