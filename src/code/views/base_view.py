import pygame
from constants import width, height


class BaseView:
    def __init__(self):
        self.design_width = width
        self.design_height = height
        self.scale_x = 1.0
        self.scale_y = 1.0
        self.elements = []  # bttons, labels, etc


    def handle_resize(self, current_width, current_height):
        """ Update scale factors and resize elements """
        self.scale_x = current_width / self.design_width
        self.scale_y = current_height / self.design_height

        for element in self.elements:
            element.resize(self.scale_x, self.scale_y)


    def draw(self, screen):
        """ Draw all elements """
        for element in self.elements:
            element.draw(screen)