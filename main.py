"""Main game loop and initialization."""

import pygame
import constants as const
from src.code.views.main_menu import MainMenu
from src.code.views.game_view import GameView
from src.code.views.loading_screen import LoadingScreen
import asyncio
from sys import exit


class Game:
    """Main game class handling initialization and the game loop."""

    def __init__(self):
        """Initializes the game window and resources."""
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
        """Adjusts the game elements when the window is resized."""
        scale = min(
            self.WIDTH / self.design_width, 
            self.HEIGHT / self.design_height
        )
        self.font = pygame.font.Font(const.font_path, int(const.font_sizes["medium"] * scale))

        if self.current_view:
            self.current_view.handle_resize(self.WIDTH, self.HEIGHT)

    def switch_view(self, view_name):
        """Switches between different game views."""
        if view_name == "main":
            pygame.mouse.set_visible(True)
            self.current_view = MainMenu(
                switch_view=self.switch_view,
                design_width=self.design_width,
                design_height=self.design_height  
            )
            pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            self.pending_view = None
        elif view_name == "game":
            self.pending_view = "game"
            self.transition_screen = LoadingScreen(self.design_width, self.design_height)
        elif view_name == "settings":
            pass
        elif view_name == "exit":
            pygame.quit()
        
        self.handle_resize()

    def handle_transition(self):
        """Handles the transition logic between views."""
        if self.pending_view == "game":
            self.transition_screen.update_fade()

            if self.transition_screen.active:
                if self.transition_screen.alpha < 255:
                    return True
                else:
                    # Start loading and disable fade-in
                    if not hasattr(self, 'load_task'):
                        self.load_task = asyncio.create_task(self.load_game_resources())
                    return True
            else:
                # Fade-out after loading
                if self.transition_screen.alpha > 0:
                    return True
                else:
                    self.transition_screen = None
                    self.pending_view = None
                    del self.load_task  # Clean up the task
                    return False

    async def load_game_resources(self):
        """Asynchronously loads game resources."""
        total_steps = 5
        for i in range(total_steps):
            await asyncio.sleep(0.3)
            self.transition_screen.update_progress((i + 1) * 20)
            self.render_transition()
            pygame.event.pump()

        # Create GameView and activate fade-out
        self.current_view = GameView(
            switch_view=self.switch_view,
            animation_paths=self.animation_paths,
            clock=self.clock,
            font=self.font
        )
        pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
        pygame.mouse.set_visible(False),
        self.transition_screen.active = False  # Start fade-out

    def render_transition(self):
        """Renders the transition screen."""
        self.window.fill(const.black)

        if self.current_view:
            self.current_view.draw(self.window)

        self.transition_screen.draw(self.window)
        pygame.display.flip()
        self.clock.tick(60)

    def update(self):
        """Updates the game state."""
        self.window.fill(const.black)
        if self.current_view:
            self.current_view.draw(self.window)
        
        if self.transition_screen:
            self.transition_screen.draw(self.window)

    async def run(self):
        """Main game loop, now asynchronous with guaranteed animation updates."""
        running = True
        last_time = pygame.time.get_ticks() / 1000.0
        
        while running:
            # Calculate delta time properly
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            # Ensure a minimum dt value to prevent animation freezing
            dt = max(dt, 0.001)  # Minimum 1ms dt
            
            # Get and process events
            events = pygame.event.get()
            pygame.event.pump()  # Process internal events
            
            await asyncio.sleep(0)  # Allow other async operations

            # Handle transition screens
            if self.transition_screen and self.handle_transition():
                self.render_transition()
                continue

            # Process events
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
                        
            # Update the current view
            if self.current_view:
                self.current_view.handle_events(events)
                if hasattr(self.current_view, "update"):
                    self.current_view.update(dt)

            # Draw everything
            self.update()
            pygame.display.flip()
            
            # Regulate frame rate
            self.clock.tick(self.FPS)

        pygame.quit()
        exit()

    def toggle_fullscreen(self):
        """Toggles fullscreen mode."""
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