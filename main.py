"""Main game loop and initialization."""

import pygame
import constants as const
from src.code.views.main_menu import MainMenu
from src.code.views.game_view import GameView
from src.code.views.loading_screen import LoadingScreen
from src.code.views.settings_menu import Settings
from src.code.views.intro_screen import IntroScreen
import asyncio
import os
from sys import exit
import json
import traceback


class Game:
    """Main game class handling initialization and the game loop."""

    def __init__(self):
        """Initializes the game window and resources."""
        pygame.init()

        self.animation_paths = {
            'idle': './src/assets/player/idle',
            'walking': './src/assets/player/walking',
            'attack': './src/assets/player/interact',
        }
        self.npc_animation_paths = {
            'walking': './src/assets/npc/walking',
            'convinced_walking': "./src/assets/npc/convinced_walk",
            'book': './src/assets/npc/reaction',
            'convinced': './src/assets/npc/convinced',
            'indecisive': './src/assets/npc/reaction',
            'closed': './src/assets/npc/closed',
        }

        self.design_width = const.width
        self.design_height = const.height

        self.WIDTH = const.width
        self.HEIGHT = const.height
        self.FPS = 60
        self.fullscreen = True  
        self.show_fps = True  # Set default value to True
        self.windowed_size = (self.WIDTH, self.HEIGHT)

        self.clock = pygame.time.Clock()
        self.font = None
        self.current_view = None
        self.transition_screen = None
        self.pending_view = None

        info = pygame.display.Info()
        self.screen_width = info.current_w
        self.screen_height = info.current_h

        flags = pygame.FULLSCREEN | pygame.RESIZABLE
        self.window = pygame.display.set_mode(
            (self.screen_width, self.screen_height), 
            flags
        )
        pygame.display.set_caption(const.title)

        const.overlay_image = pygame.image.load("src/assets/menu/overlay.png").convert_alpha()
        
        menu_frames_path = "src/assets/menu/frames"
        menu_frames = sorted([f for f in os.listdir(menu_frames_path) if f.endswith(('.png', '.jpg'))])
        
        if menu_frames and len(menu_frames) > const.static_menu_frame_index:
            static_frame_file = menu_frames[const.static_menu_frame_index]
            const.static_menu_frame = pygame.image.load(f"{menu_frames_path}/{static_frame_file}").convert_alpha()
        else:
            if menu_frames:
                const.static_menu_frame = pygame.image.load(f"{menu_frames_path}/{menu_frames[0]}").convert_alpha()
        
        self.intro_screen = IntroScreen(
            design_width=self.design_width,
            design_height=self.design_height,
            current_width=self.screen_width,
            current_height=self.screen_height
        )
        self.showing_intro = True
        self.menu_loaded = False
        
        self.handle_resize()

    def handle_resize(self):
        """Adjusts the game elements when the window is resized."""
        scale = min(self.screen_width / self.design_width, self.screen_height / self.design_height)
        self.font = pygame.font.Font(const.font_path, int(const.font_sizes["medium"] * scale))
        
        if hasattr(self, 'current_view'):
            if hasattr(self.current_view, 'handle_resize'):
                self.current_view.handle_resize(self.screen_width, self.screen_height)
            
            if hasattr(self.current_view, 'player') and hasattr(self.current_view, 'camera'):
                self.current_view.player.rect.center = (self.screen_width // 2, self.screen_height // 2)
                
                if hasattr(self.current_view.player, '_float_pos'):
                    self.current_view.player._float_pos.x = self.current_view.player.rect.centerx
                    self.current_view.player._float_pos.y = self.current_view.player.rect.centery
                
                self.current_view.camera.force_center = True

    def switch_view(self, view_name):
        """Switches between different game views."""
        if view_name == "main":
            pygame.mouse.set_visible(True)
            
            if hasattr(self, 'saved_game_view'):
                self.pending_view = "main"
                self.transition_screen = LoadingScreen(
                    design_width = self.design_width, 
                    design_height = self.design_height,
                    current_width = self.screen_width,
                    current_height = self.screen_height
                )
            else:
                if not hasattr(self, 'main_menu'):
                    self.main_menu = MainMenu(
                        switch_view = self.switch_view,
                        design_width = self.screen_width,
                        design_height = self.screen_height  
                    )
                    
                self.current_view = self.main_menu
                pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
                self.pending_view = None
        elif view_name == "settings_to_main":
            pygame.mouse.set_visible(True)
            self.pending_view = "settings_to_main"
            self.transition_screen = LoadingScreen(
                design_width = self.design_width, 
                design_height = self.design_height,
                current_width = self.screen_width,
                current_height = self.screen_height
            )
        elif view_name == "settings":
            pygame.mouse.set_visible(True)
            self.pending_view = "settings"
            self.transition_screen = LoadingScreen(
                design_width = self.design_width, 
                design_height = self.design_height,
                current_width = self.screen_width,
                current_height = self.screen_height
            )
        elif view_name == "game":
            self.pending_view = "game"
            self.transition_screen = LoadingScreen(
                design_width = self.design_width, 
                design_height = self.design_height,
                current_width = self.screen_width,
                current_height = self.screen_height
            )
        elif view_name == "ingame_settings":
            pygame.mouse.set_visible(True)

            if isinstance(self.current_view, GameView):
                self.saved_game_view = self.current_view
            
            self.current_view = Settings(
                switch_view = self.switch_view,
                design_width = self.screen_width,
                design_height = self.screen_height,
                get_game_state = self.get_game_state,
                toggle_fullscreen = None,
                is_ingame = True,  
                return_to_game = lambda: self.return_to_game()
            )
            pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            self.pending_view = None
        elif view_name == "exit":
            pygame.quit()
            exit()
        
        self.handle_resize()

    def get_game_state(self):
        """Returns a dictionary with current game state values."""
        return {
            'fullscreen': self.fullscreen,
            'show_fps': self.show_fps
        }

    def handle_transition(self):
        """Handles the transition logic between views."""
        if self.pending_view == "game":
            self.transition_screen.update_fade()
            
            if self.transition_screen.active:
                if self.transition_screen.alpha < 255:
                    return True
                else:
                    if not hasattr(self, 'load_task'):
                        self.load_task = asyncio.create_task(self.load_game_resources())
                    return True
            # We're in fade-out (decreasing alpha)
            else:
                # If alpha > 0, fade-out is in progress
                if self.transition_screen.alpha > 0:
                    return True
                # If alpha = 0, fade-out is complete
                else:
                    # Clean transition variables
                    self.transition_screen = None
                    self.pending_view = None
                    if hasattr(self, 'load_task'):
                        del self.load_task
                    return False
        elif self.pending_view == "main":
            self.transition_screen.update_fade()

            if self.transition_screen.active:
                if self.transition_screen.alpha < 255:
                    return True
                else:
                    self.transition_screen.active = False
                    self.current_view = MainMenu(
                        switch_view = self.switch_view,
                        design_width = self.screen_width,
                        design_height = self.screen_height  
                    )
                    pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
                    return True
            else:
                if self.transition_screen.alpha > 0:
                    return True
                else:
                    self.transition_screen = None
                    self.pending_view = None
                    if hasattr(self, 'saved_game_view'):
                        delattr(self, 'saved_game_view')
                    return False
        elif self.pending_view == "settings_to_main":
            self.transition_screen.update_fade()

            if self.transition_screen.active:
                if self.transition_screen.alpha < 255:
                    return True
                else:
                    self.transition_screen.active = False
                    self.current_view = MainMenu(
                        switch_view = self.switch_view,
                        design_width = self.screen_width,
                        design_height = self.screen_height  
                    )
                    pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
                    return True
            else:
                if self.transition_screen.alpha > 0:
                    return True
                else:
                    self.transition_screen = None
                    self.pending_view = None
                    return False
        elif self.pending_view == "settings":
            self.transition_screen.update_fade()

            if self.transition_screen.active:
                if self.transition_screen.alpha < 255:
                    return True
                else:
                    self.transition_screen.active = False
                    self.current_view = Settings(
                        switch_view = self.switch_view,
                        design_width = self.screen_width,
                        design_height = self.screen_height,
                        get_game_state = self.get_game_state,
                        toggle_fullscreen = self.toggle_fullscreen
                    )
                    pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
                    return True
            else:
                if self.transition_screen.alpha > 0:
                    return True
                else:
                    self.transition_screen = None
                    self.pending_view = None
                    return False

    async def load_game_resources(self):
        """Loads game resources asynchronously."""
        try:
            # Create loading screen if not exists
            if not hasattr(self, 'transition_screen') or not self.transition_screen:
                self.transition_screen = LoadingScreen(
                    design_width=self.design_width,
                    design_height=self.design_height,
                    current_width=self.screen_width,
                    current_height=self.screen_height
                )
                self.transition_screen.active = True
                
            # Emulate loading with progress
            steps = 10
            for i in range(steps+1):
                progress = i / steps
                if hasattr(self, 'transition_screen') and self.transition_screen:
                    self.transition_screen.update_progress(progress)
                    
                # Create GameView at 80% of the load
                if i == int(steps * 0.8):
                    try:
                        # Create GameView with the parameters it expects in its constructor
                        self.current_view = GameView(
                            switch_view=self.switch_view,
                            animation_paths=self.animation_paths,
                            npc_animation_paths=self.npc_animation_paths,
                            clock=self.clock,
                            font=self.font,
                            show_fps=self.show_fps
                        )
                        
                        # Check if game state needs to be restored
                        if os.path.exists("src/save/current_game.json"):
                            try:
                                with open("src/save/current_game.json", "r") as f:
                                    saved_game = json.load(f)
                                    if "player_position" in saved_game:
                                        player_pos = saved_game["player_position"]
                                        self.current_view.player.position.x = player_pos[0]
                                        self.current_view.player.position.y = player_pos[1]
                            except Exception as e:
                                pass
                    except Exception as e:
                        # Keep track of errors but silently log them
                        traceback.print_exc()
            
            # Load complete, start fade-out
            # Start the fade-out
            if hasattr(self, 'transition_screen') and self.transition_screen:
                self.transition_screen.start_fade_out()
            
        except Exception as e:
            # Keep track of fatal errors in loading
            traceback.print_exc()

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
            # Update show_fps setting from settings menu if available
            if isinstance(self.current_view, Settings):
                self.show_fps = self.current_view.show_fps
            
            self.current_view.draw(self.window)
        
        if self.transition_screen:
            self.transition_screen.draw(self.window)

    async def preload_main_menu(self):
        """Asynchronously preloads game resources for main menu."""
        self.main_menu = MainMenu(
            switch_view = self.switch_view,
            design_width = self.screen_width,
            design_height = self.screen_height  
        )

        self.menu_loaded = True

    async def preload_view(self, view_name):
        """Asynchronously loads game resources between views."""
        await asyncio.sleep(0.05)
        
        if view_name == "settings":
            settings_view = Settings(
                switch_view = self.switch_view,
                design_width = self.screen_width,
                design_height = self.screen_height,
                get_game_state = self.get_game_state,
                toggle_fullscreen = self.toggle_fullscreen
            )
            for i in range(3):
                await asyncio.sleep(0.1)
                if self.transition_screen:
                    self.transition_screen.update_progress((i + 1) * 33)

            while self.transition_screen and self.transition_screen.alpha < 255:
                await asyncio.sleep(0.01)
                
            self.current_view = settings_view
            pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            if self.transition_screen:
                self.transition_screen.active = False
                
        elif view_name == "settings_to_main":
            if not hasattr(self, 'main_menu'):
                self.main_menu = MainMenu(
                    switch_view = self.switch_view,
                    design_width = self.screen_width,
                    design_height = self.screen_height
                )
                
            for i in range(3):
                await asyncio.sleep(0.1)
                if self.transition_screen:
                    self.transition_screen.update_progress((i + 1) * 33)

            while self.transition_screen and self.transition_screen.alpha < 255:
                await asyncio.sleep(0.01)
                
            self.current_view = self.main_menu
            pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            if self.transition_screen:
                self.transition_screen.active = False
                
        elif view_name == "main_from_game":
            if not hasattr(self, 'main_menu'):
                self.main_menu = MainMenu(
                    switch_view = self.switch_view,
                    design_width = self.screen_width,
                    design_height = self.screen_height  
                )
                
            for i in range(5):
                await asyncio.sleep(0.1)
                if self.transition_screen:
                    self.transition_screen.update_progress((i + 1) * 20)
            
            while self.transition_screen and self.transition_screen.alpha < 255:
                await asyncio.sleep(0.01)

            self.current_view = self.main_menu
            pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            if self.transition_screen:
                self.transition_screen.active = False

            if hasattr(self, 'saved_game_view'):
                delattr(self, 'saved_game_view')
                
        elif view_name == "ingame_settings":
            ingame_settings = Settings(
                switch_view = self.switch_view,
                design_width = self.screen_width,
                design_height = self.screen_height,
                get_game_state = self.get_game_state,
                toggle_fullscreen = None,
                is_ingame = True,  
                return_to_game = lambda: self.return_to_game()
            )
            
            for i in range(3):
                await asyncio.sleep(0.1)
                if self.transition_screen:
                    self.transition_screen.update_progress((i + 1) * 33)

            while self.transition_screen and self.transition_screen.alpha < 255:
                await asyncio.sleep(0.01)

            self.current_view = ingame_settings
            pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            if self.transition_screen:
                self.transition_screen.active = False
                self.pending_view = None

    def finish_intro(self):
        """Go to main menu after resources load."""
        self.showing_intro = False
        self.current_view = self.main_menu
        pygame.event.set_allowed([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])

    def toggle_fullscreen(self):
        """Toggles fullscreen mode."""
        self.fullscreen = not self.fullscreen
        
        if self.fullscreen:
            self.windowed_size = (self.screen_width, self.screen_height)
            self.window = pygame.display.set_mode(
                (0, 0),
                pygame.FULLSCREEN
            )
            self.screen_width, self.screen_height = self.window.get_size()
        else:
            self.window = pygame.display.set_mode(
                self.windowed_size,
                pygame.RESIZABLE
            )
            self.screen_width, self.screen_height = self.windowed_size
        

        if hasattr(self, 'current_view') and hasattr(self.current_view, 'handle_fullscreen_change'):
            self.current_view.handle_fullscreen_change(self.screen_width, self.screen_height, self.fullscreen)
        else:
            if hasattr(self, 'current_view') and hasattr(self.current_view, 'handle_resize'):
                self.current_view.handle_resize(self.screen_width, self.screen_height)
        
        # Update the screen size of the transition views
        if self.transition_screen:
            self.transition_screen.update_screen_size(self.screen_width, self.screen_height)

    def return_to_game(self):
        """Returns to the saved game view after closing in-game settings."""
        if hasattr(self, 'saved_game_view'):
            self.current_view = self.saved_game_view
            pygame.mouse.set_visible(False)
            pygame.event.set_blocked([pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
            self.pending_view = None


    async def run(self):
        """Main game loop, now asynchronous with guaranteed animation updates."""
        running = True
        last_time = pygame.time.get_ticks() / 1000.0

        asyncio.create_task(self.preload_main_menu())
        
        while running:
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            dt = max(dt, 0.001) 
            
            events = pygame.event.get()
            pygame.event.pump()
            
            await asyncio.sleep(0)  # Allow other async operations

            if self.showing_intro:
                self.intro_screen.update(dt)
                self.intro_screen.draw(self.window)
                pygame.display.flip()
                
                if self.intro_screen.completed and self.menu_loaded:
                    self.finish_intro()

                self.clock.tick(self.FPS)
                continue

            # Update menu animation if we are in the main menu
            if isinstance(self.current_view, MainMenu) and hasattr(self.current_view, 'menu_animation'):
                self.current_view.menu_animation.update(dt)

            # Simplified transition handling
            if self.transition_screen:
                self.transition_screen.update_fade()
                if self.handle_transition():
                    if hasattr(self.current_view, "update"):
                        self.current_view.update(dt)
                    self.current_view.draw(self.window)
                    self.transition_screen.draw(self.window)
                    pygame.display.flip()
                    self.clock.tick(self.FPS)
                    continue

            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.VIDEORESIZE:
                    if not self.fullscreen:
                        self.screen_width, self.screen_height = event.w, event.h
                        self.windowed_size = (self.screen_width, self.screen_height)
                        self.handle_resize()

            if self.current_view:
                self.current_view.handle_events(events)
                # If current_view has an update method, call it
                if hasattr(self.current_view, "update"):
                    self.current_view.update(dt)

            # Update the screen for the normal case
            self.window.fill((0, 0, 0))
            if self.current_view:
                self.current_view.draw(self.window)
            if self.transition_screen:
                self.transition_screen.draw(self.window)
            pygame.display.flip()
            
            self.clock.tick(self.FPS)

        pygame.quit()
        exit()


if __name__ == '__main__':
    game = Game()
    asyncio.run(game.run())