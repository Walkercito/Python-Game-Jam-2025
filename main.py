import pygame
import constants as const

from src.code.views.main_menu import MainMenu


class Game:
    def __init__(self):
        pygame.init()

        # base scale
        self.design_width = const.width
        self.design_height = const.height

        self.WIDTH = const.width
        self.HEIGHT = const.height
        self.FPS = 60
        self.fullscreen = False
        self.windowed_size = (self.WIDTH, self.HEIGHT)
        
        self.clock = pygame.time.Clock()
        self.font = None  # will initialize later

        self.window = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption(const.title)

        self.current_view = None
        self.switch_view("main")  # start with main menu
        self.handle_resize()


    def handle_resize(self):
        """ Scale to match new window size """
        scale = min(
            self.WIDTH / self.design_width, 
            self.HEIGHT / self.design_height
        )
        self.font = pygame.font.Font(None, int(36 * scale))

        if self.current_view:
            self.current_view.handle_resize(self.WIDTH, self.HEIGHT)


    def switch_view(self, view_name):
        """ Switch between views"""
        if view_name == "main":
            self.current_view = MainMenu(self.switch_view)
        elif view_name == "settings":
            pass
        elif view_name == "exit":
            pygame.quit()
        
        if self.current_view:
            self.current_view.handle_resize(self.WIDTH, self.HEIGHT)


    def update(self):
        """ Update game logic """
        self.window.fill(const.black)
        
        # draw current view
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
                
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.WIDTH, self.HEIGHT = event.w, event.h
                        self.windowed_size = (self.WIDTH, self.HEIGHT)
                        self.handle_resize()
                
                elif event.type == pygame.KEYDOWN:
                    # toggle fullscreen with f11 or f 
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
                        
                        # update dimaensions
                        self.WIDTH, self.HEIGHT = self.window.get_size()
                        self.handle_resize()

                if self.current_view:
                    self.current_view.handle_events(events)

            self.update()
            pygame.display.flip()
        
        pygame.quit()


if __name__ == '__main__':
    game = Game()
    game.run()