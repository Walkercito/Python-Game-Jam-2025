import pygame
from .button import Button


class MainMenu:
    def __init__(self, switch_view):
        self.switch_view = switch_view
        self.buttons = []
        self.create_buttons()


    def create_buttons(self):
        button_border = "src/assets/PNG/Default/Border/panel-border-003.png"
        
        self.buttons.append(Button(
            text = "Play",
            x = 300, y = 200,
            width = 200, height = 60,
            on_click = lambda: print("Starting game"),
            image_path = button_border,
            border_size = 16,
            use_9slice = True
        ))
        self.buttons.append(Button(
            text = "Settings",
            x = 300, y = 270,
            width = 200, height = 60,
            on_click = lambda: self.switch_view("settings"),
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))
        self.buttons.append(Button(
            text = "Credits",
            x = 300, y = 340,
            width = 200, height = 60,
            on_click = lambda: self.switch_view("credits"),
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))
        self.buttons.append(Button(
            text = "Exit",
            x = 300, y = 410,
            width = 200, height = 60,
            on_click = lambda: self.switch_view("exit"),
            image_path = button_border,
            border_size = 12,
            use_9slice = True
        ))


    def handle_events(self, events):
        """ Manage window events """
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
        """ Scale to match new window size """
        scale_x = new_width / 1020  
        scale_y = new_height / 620  
        
        for button in self.buttons:
            button.resize(scale_x, scale_y)


    def draw(self, screen):
        """ Draw all menu elements """
        for button in self.buttons:
            button.draw(screen)