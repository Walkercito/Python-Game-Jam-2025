import pygame
import constants as const
from src.code.views.main_menu import MainMenu
from src.code.views.loading_screen import LoadingScreen
import asyncio

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
        self.current_view = None
        self.transition_screen = None
        self.pending_view = None

        self.window = pygame.display.set_mode(
            (self.WIDTH, self.HEIGHT), 
            pygame.RESIZABLE
        )
        pygame.display.set_caption(const.title)
        
        self.switch_view("main")
        self.handle_resize()


    def handle_resize(self):
        scale = min(
            self.WIDTH / self.design_width, 
            self.HEIGHT / self.design_height
        )
        self.font = pygame.font.Font(const.font_path, int(const.font_sizes["medium"] * scale))

        if self.current_view:
            self.current_view.handle_resize(self.WIDTH, self.HEIGHT)


    def switch_view(self, view_name):
        if view_name == "main":
            self.current_view = MainMenu(
                switch_view = self.switch_view,
                design_width = self.design_width,
                design_height = self.design_height  
            )
            self.pending_view = None
        elif view_name == "game":
            self.pending_view = "game"
            self.transition_screen = LoadingScreen(self.design_width, self.design_height)
            # Crear una tarea asíncrona para la carga
            asyncio.create_task(self.load_game_resources())
        elif view_name == "settings":
            pass
        elif view_name == "exit":
            pygame.quit()
        
        self.handle_resize()


    def handle_transition(self):
        """Maneja la lógica de transición entre vistas"""
        if self.pending_view == "game":
            self.transition_screen.update_fade()

            if self.transition_screen.active:
                if self.transition_screen.alpha < 255:
                    return True
                else:
                    self.load_game_resources()
                    return True

            else:
                if self.transition_screen.alpha > 0:
                    return True
                else:
                    self.transition_screen = None
                    return False


    async def load_game_resources(self):
        """Carga asíncrona de los recursos del juego"""
        total_steps = 5
        for i in range(total_steps):
            await asyncio.sleep(0.3)  # Simulando carga
            self.transition_screen.update_progress((i + 1) * 20)
            self.render_transition()
            pygame.event.pump()

        # Crear la vista del juego cuando la carga termine
        self.current_view = GameView(
            switch_view=self.switch_view,
            animation_paths=self.animation_paths,
            clock=self.clock,
            font=self.font
        )
        self.transition_screen.active = False


    def render_transition(self):
        """Renderiza la pantalla de transición"""
        self.window.fill(const.black)

        if self.current_view:
            self.current_view.draw(self.window)

        self.transition_screen.draw(self.window)
        pygame.display.flip()
        self.clock.tick(60)


    def update(self):
        self.window.fill(const.black)
        if self.current_view:
            self.current_view.draw(self.window)
        
        if self.transition_screen:
            self.transition_screen.draw(self.window)


    async def run(self):
        """Método principal del juego, ahora asíncrono"""
        running = True
        while running:
            dt = self.clock.tick(self.FPS) / 1000.0
            events = pygame.event.get()

            if self.transition_screen and self.handle_transition():
                self.render_transition()
                continue

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.WIDTH, self.HEIGHT = event.w, event.h
                        self.windowed_size = (self.WIDTH, self.HEIGHT)
                        self.handle_resize()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_f:
                        self.toggle_fullscreen()
                if self.current_view:
                    self.current_view.handle_events(events)
                    if hasattr(self.current_view, "update"):
                        self.current_view.update(dt)

            self.update()
            pygame.display.flip()

        pygame.quit()


    def toggle_fullscreen(self):
        """Alternar modo pantalla completa"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.windowed_size = (self.WIDTH, self.HEIGHT)
            self.window = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.window = pygame.display.set_mode(self.windowed_size, pygame.RESIZABLE)
        
        self.WIDTH, self.HEIGHT = self.window.get_size()
        self.handle_resize()



if __name__ == '__main__':
    game = Game()
    asyncio.run(game.run())