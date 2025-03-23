import pygame 
from .button import Button


class Settings:
    def __init__(self, switch_view):
        self.switch_view = switch_view
        self.buttons = []
        self.create_buttons()