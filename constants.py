"""Global constants for the game."""

import pygame

width = 1020
height = 620
title = "Awaking"

white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)

tmx_data = None

font_path = "src/assets/fonts/SpecialElite-Regular.ttf"
font_sizes = {
    "small": 24,
    "medium": 36,
    "large": 48
}

font_colors = {
    "default": black,
    "button": gray,
    "title": white,
    "subtitle": gray
}


overlay_image = None
static_menu_frame = None
use_static_menu = False 
static_menu_frame_index = 17

# Lighting system settings
use_prerendered_lights = True  # Por defecto usar luces pre-renderizadas para mejor rendimiento