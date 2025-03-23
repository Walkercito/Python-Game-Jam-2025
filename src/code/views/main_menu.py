import pygame
from .button import Button


class MainMenu:
    def __init__(self, switch_view):
        self.switch_view = switch_view
        self.buttons = []
        self.create_buttons()


    def create_buttons(self):
        self.buttons.append(Button(
            text = "Play",
            x = 300, y = 200,
            width = 200, height = 50,
            on_click = lambda: print("Starting game")
        ))
        self.buttons.append(Button(
            text = "Settings",
            x = 300, y = 300,
            width = 200, height = 50,
            on_click = lambda: self.switch_view("settings")
        ))
        self.buttons.append(Button(
            text = "Credits",
            x = 300, y = 400,
            width = 200, height = 50,
            on_click = lambda: self.switch_view("credits")
        ))
        self.buttons.append(Button(
            text = "Exit",
            x = 300, y = 500,
            width = 200, height = 50,
            on_click = lambda: self.switch_view("exit")
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