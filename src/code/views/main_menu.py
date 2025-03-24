"""Main menu with interactive buttons."""

import pygame
from .button import Button
import constants as const


class MainMenu:
    """Handles the main menu screen and its buttons."""

    def __init__(self, switch_view, design_width, design_height):
        """Initializes the main menu with buttons and layout."""
        self.switch_view = switch_view
        self.design_width = design_width 
        self.design_height = design_height  
        self.buttons = []
        self.title_font = pygame.font.Font(const.font_path, const.font_sizes["large"] + 20)
        
        # Use the globally loaded overlay image
        self.overlay = pygame.transform.scale(const.overlay_image, (design_width, design_height))
        self.overlay_rect = self.overlay.get_rect()
        
        self.create_buttons()

    def create_buttons(self):
        """Creates and positions the menu buttons."""
        button_border = "src/assets/borders/PNG/Default/Border/panel-border-010.png"
        
        button_height = 60
        spacing = 20
        
        start_y = 200
        
        self.buttons.append(Button(
            text = "Play",
            x = 50, y = start_y,
            width = 200, height = button_height,
            on_click = lambda: self.switch_view("game"),
            image_path = button_border,
            border_size = 16,
            use_9slice = True
        ))
        self.buttons.append(Button(
            text = "Settings",
            x = 50, y = start_y + (button_height + spacing),
            width = 200, height = button_height,
            on_click = lambda: self.switch_view("settings"),
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))
        self.buttons.append(Button(
            text = "Credits",
            x = 50, y = start_y + 2 * (button_height + spacing),
            width = 200, height = button_height,
            on_click = lambda: self.switch_view("credits"),
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))
        self.buttons.append(Button(
            text = "Exit",
            x = 50, y = start_y + 3 * (button_height + spacing),
            width = 200, height = button_height,
            on_click = lambda: self.switch_view("exit"),
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))

    def handle_events(self, events):
        """Handles input events for the menu."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    if button.rect.collidepoint(mouse_pos):
                        button.on_click()

            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                for button in self.buttons:
                    button.check_hover(mouse_pos)

    def handle_resize(self, new_width, new_height):
        """Adjusts the menu layout when the window is resized."""
        scale_x = new_width / self.design_width
        scale_y = new_height / self.design_height

        # Resize overlay image to fit the screen
        self.overlay = pygame.transform.scale(const.overlay_image, (new_width, new_height))
        self.overlay_rect = self.overlay.get_rect()
        
        for button in self.buttons:
            button.resize(scale_x, scale_y)

    def draw(self, screen):
        """Draws the menu and its buttons."""
        # Draw background
        screen.fill((30, 30, 30))
        
        # Draw overlay image
        screen.blit(self.overlay, self.overlay_rect)
        
        title_text = self.title_font.render("Awaking", True, (255, 255, 255))
        title_rect = title_text.get_rect(x=50, y=80)
        screen.blit(title_text, title_rect)
        
        for button in self.buttons:
            button.draw(screen)
        
        if hasattr(self, 'transition_overlay'):
            screen.blit(self.transition_overlay, (0, 0))