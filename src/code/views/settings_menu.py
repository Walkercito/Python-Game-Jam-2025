"""Settings view for customization."""

import pygame 
from .button import Button
import constants as const
import os


class MenuAnimation:
    """Manage the animation of menu frames."""
    
    def __init__(self, frame_path, default_size):
        self.frame = pygame.image.load(frame_path).convert_alpha()
        self.default_size = default_size
        self.scaled_frame = pygame.transform.scale(self.frame, default_size)
        self.frame_rect = self.scaled_frame.get_rect()
        
    def resize(self, new_size):
        """Resize frame to a new size."""
        self.scaled_frame = pygame.transform.scale(self.frame, new_size)
        self.frame_rect = self.scaled_frame.get_rect()
    
    def get_current_frame(self):
        """Gets the current scaled frame"""
        return self.scaled_frame


class Settings:
    """Handles the settings menu screen and its options."""

    def __init__(self, switch_view, design_width=const.width, design_height=const.height, 
                get_game_state=None, toggle_fullscreen=None, is_ingame=False, return_to_game=None):
        """Initializes the settings menu with buttons and options."""
        self.switch_view = switch_view
        self.design_width = design_width
        self.design_height = design_height
        self.get_game_state = get_game_state
        self.toggle_fullscreen = toggle_fullscreen
        self.is_ingame = is_ingame
        self.return_to_game = return_to_game
        
        self.buttons = []
        self.title_font = pygame.font.Font(const.font_path, const.font_sizes["large"])
        self.subtitle_font = pygame.font.Font(const.font_path, const.font_sizes["medium"])
        self.option_font = pygame.font.Font(const.font_path, const.font_sizes["small"])
        
        # Use the globally loaded overlay image
        self.overlay = pygame.transform.scale(const.overlay_image, (design_width, design_height))
        self.overlay_rect = self.overlay.get_rect()

        # Initialize menu animation for static menu frame
        self.static_menu_animation = MenuAnimation(
            frame_path="src/assets/menu/frames/frame_0017.jpg",
            default_size=(design_width, design_height)
        )
        
        # Get current settings from game state
        self.fullscreen = False
        self.show_fps = True
        self.use_baked_lights = False
        
        if self.get_game_state:
            game_state = self.get_game_state()
            self.fullscreen = game_state.get('fullscreen', False)
            self.show_fps = game_state.get('show_fps', True)
            self.use_baked_lights = game_state.get('use_baked_lights', False)
        
        self.create_buttons()
    
    def create_buttons(self):
        """Creates and positions the settings buttons."""
        button_border = "src/assets/borders/PNG/Default/Border/panel-border-010.png"
        
        # Back button with different behavior based on if accessed from game or main menu
        back_text = "Resume" if self.is_ingame else "Back"
        back_action = self.return_to_game if self.is_ingame else lambda: self.switch_view("settings_to_main")
        
        self.buttons.append(Button(
            text = back_text,
            x = 50,
            y = self.design_height - 80,
            width=200,
            height = 60,
            on_click = back_action,
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))
        
        if self.is_ingame:
            self.buttons.append(Button(
                text = "Menu",
                x = self.design_width - 250,
                y = self.design_height - 80,
                width = 200,
                height = 60,
                on_click = lambda: self.switch_view("main"),
                image_path = button_border,
                border_size = 12,
                use_9slice = True
            ))
        
        if not self.is_ingame and self.toggle_fullscreen is not None:
            fullscreen_text = "Fullscreen: ON" if self.fullscreen else "Fullscreen: OFF"
            self.buttons.append(Button(
                text = fullscreen_text,
                x = self.design_width//2 - 150,
                y = 200,
                width = 300,
                height = 60,
                on_click = self.toggle_fullscreen_option,
                image_path = button_border,
                border_size = 12,
                use_9slice = True
            ))
        elif self.is_ingame:
            self.buttons.append(Button(
                text = "Fullscreen",
                x = self.design_width//2 - 150,
                y = 200,
                width = 300,
                height = 60,
                on_click = None,
                image_path = button_border,
                border_size = 12,
                use_9slice = True,
                disabled = True
            ))
        
        y_position = 300 
        
        fps_text = "Show FPS: ON" if self.show_fps else "Show FPS: OFF"
        self.buttons.append(Button(
            text = fps_text,
            x = self.design_width//2 - 150,
            y = y_position,
            width = 300,
            height = 60,
            on_click = self.toggle_fps_option,
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))
        
        y_position += 200
        baked_lights_text = "Baked Lights: ON" if self.use_baked_lights else "Baked Lights: OFF"
        if not self.is_ingame:
            self.buttons.append(Button(
                text = baked_lights_text,
                x = self.design_width//2 - 150,
                y = y_position,
                width = 300,
                height = 60,
                on_click = self.toggle_baked_lights_option,
                image_path = button_border,
                border_size = 12,
                use_9slice = True
            ))
        
        y_position += 100
        static_menu_text = "Static menu: ON" if const.use_static_menu else "Static menu: OFF"
        
        if not self.is_ingame:
            self.static_menu_btn = Button(
                text = static_menu_text,
                x = self.design_width//2 - 150,
                y = 400,
                width = 300,
                height = 60,
                on_click = self.toggle_static_menu_option,
                image_path = button_border,
                border_size = 12,
                use_9slice = True
            )
            self.buttons.append(self.static_menu_btn)
            # Store the index of static menu button for easier access
            self.static_menu_btn_index = len(self.buttons) - 1
    
    def toggle_fullscreen_option(self):
        """Toggles the fullscreen setting and updates the button text."""
        self.fullscreen = not self.fullscreen
        
        fullscreen_text = "Fullscreen: ON" if self.fullscreen else "Fullscreen: OFF"
        self.buttons[1].text = fullscreen_text
        
        if self.toggle_fullscreen:
            self.toggle_fullscreen()
    
    def toggle_fps_option(self):
        """Toggles the show FPS setting and updates the button text."""
        self.show_fps = not self.show_fps
        
        fps_text = "Show FPS: ON" if self.show_fps else "Show FPS: OFF"
        # Actualizar el índice del botón FPS (ahora no es el último debido al botón de Baked Lights)
        fps_button_index = 3 if self.is_ingame else 2
        self.buttons[fps_button_index].text = fps_text
        
    def toggle_baked_lights_option(self):
        """Toggles the baked lights setting and updates the button text."""
        import constants as const
        
        self.use_baked_lights = not self.use_baked_lights
        const.use_baked_lights = self.use_baked_lights
        
        baked_lights_text = "Baked Lights: ON" if self.use_baked_lights else "Baked Lights: OFF"
        # El botón de Baked Lights es el penultimo (antes del Static Menu)
        baked_lights_button_index = 4 if self.is_ingame else 3
        self.buttons[baked_lights_button_index].text = baked_lights_text
    
    def toggle_static_menu_option(self):
        """Toggles the static menu setting and updates the button text."""
        const.use_static_menu = not const.use_static_menu
        

        self.static_menu_btn.text = "Static menu: ON" if const.use_static_menu else "Static menu: OFF"
    
    def handle_events(self, events):
        """Handles input events for the settings menu."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    button.check_click(mouse_pos)
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    button.check_hover(mouse_pos)
                    
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.is_ingame:
                    self.return_to_game()
                else:
                    self.switch_view("settings_to_main")
    
    def handle_resize(self, new_width, new_height):
        """Adjusts the menu layout when the window is resized."""
        # Resize overlay image to fit the screen
        self.overlay = pygame.transform.scale(const.overlay_image, (new_width, new_height))
        self.overlay_rect = self.overlay.get_rect()

        # Resize the static menu frame using the animation class
        self.static_menu_animation.resize((new_width, new_height))
        
        # Adjust the back button position
        self.buttons[0].rect.y = new_height - 80
        
        # Adjust ingame menu button position if applicable
        if self.is_ingame and len(self.buttons) > 1:
            self.buttons[1].rect.x = new_width - 250
            self.buttons[1].rect.y = new_height - 80
            
        # Center all option buttons
        fullscreen_button_index = 2 if self.is_ingame else 1
        fps_button_index = 3 if self.is_ingame else 2
        baked_lights_button_index = 4 if self.is_ingame else 3
        
        if len(self.buttons) > fullscreen_button_index:
            self.buttons[fullscreen_button_index].rect.centerx = new_width // 2
            
        if len(self.buttons) > fps_button_index:
            self.buttons[fps_button_index].rect.centerx = new_width // 2
            
        if len(self.buttons) > baked_lights_button_index:
            self.buttons[baked_lights_button_index].rect.centerx = new_width // 2
        
        # Properly center the static menu button
        if not self.is_ingame and hasattr(self, 'static_menu_btn_index'):
            static_btn = self.buttons[self.static_menu_btn_index]
            static_btn.rect.centerx = new_width // 2
            static_btn.rect.x = new_width // 2 - static_btn.rect.width // 2
    
    def draw(self, screen):
        """Draws the settings menu and its options."""
        screen.fill((30, 30, 30))
        
        # Draw static menu frame using the animation class
        static_frame = self.static_menu_animation.get_current_frame()
        screen.blit(static_frame, self.static_menu_animation.frame_rect)
        
        # Draw overlay image
        screen.blit(self.overlay, self.overlay_rect)
        
        title_text = self.title_font.render("Settings", True, (255, 255, 255))
        title_rect = title_text.get_rect(centerx=screen.get_width()//2, y=50)
        screen.blit(title_text, title_rect)
        
        for button in self.buttons:
            button.draw(screen)