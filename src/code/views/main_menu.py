"""Main menu with interactive buttons."""

import pygame
from .button import Button


class MainMenu:
    """Handles the main menu screen and its buttons."""

    def __init__(self, switch_view, design_width, design_height):
        """Initializes the main menu with buttons and layout."""
        self.switch_view = switch_view
        self.design_width = design_width 
        self.design_height = design_height  
        self.buttons = []
        self.create_buttons()

    def create_buttons(self):
        """Creates and positions the menu buttons."""
        button_border = "src/assets/borders/PNG/Default/Border/panel-border-010.png"
        
        button_count = 4
        button_height = 60
        spacing = 10
        total_height = (button_height * button_count) + (spacing * (button_count - 1))
        start_y = (self.design_height - total_height) // 2 
        
        self.buttons.append(Button(
            text="Play",
            x=50, y=start_y,
            width=200, height=button_height,
            on_click=lambda: self.switch_view("game"),
            image_path=button_border,
            border_size=16,
            use_9slice=True
        ))
        self.buttons.append(Button(
            text="Settings",
            x=50, y=start_y + (button_height + spacing),
            width=200, height=button_height,
            on_click=lambda: self.switch_view("settings"),
            image_path=button_border,
            border_size=12,
            use_9slice=True
        ))
        self.buttons.append(Button(
            text="Credits",
            x=50, y=start_y + 2 * (button_height + spacing),
            width=200, height=button_height,
            on_click=lambda: self.switch_view("credits"),
            image_path=button_border,
            border_size=12,
            use_9slice=True
        ))
        self.buttons.append(Button(
            text="Exit",
            x=50, y=start_y + 3 * (button_height + spacing),
            width=200, height=button_height,
            on_click=lambda: self.switch_view("exit"),
            image_path=button_border,
            border_size=12,
            use_9slice=True
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

        for button in self.buttons:
            button.resize(scale_x, scale_y)

    def draw(self, screen):
        """Draws the menu and its buttons."""
        for button in self.buttons:
            button.draw(screen)
        
        if hasattr(self, 'transition_overlay'):
            screen.blit(self.transition_overlay, (0, 0))