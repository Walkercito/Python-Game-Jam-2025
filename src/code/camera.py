"""Camera system for following the player. Thx to Clear Code for the tutorial"""

import pygame


def lerp(a, b, t):
    """Linear interpolation between a and b by t amount."""
    return a + (b - a) * t


class Camera:
    """A simple camera that follows the player with an optional dead zone."""
    
    def __init__(self, width, height, dead_zone_percent=0.1):
        """Initializes the camera with dimensions and parameters.
        
        Args:
            width: Viewport width
            height: Viewport height
            dead_zone_percent: Percentage of screen where player can move without camera following
        """
        self.width = width
        self.height = height
        self.offset = pygame.math.Vector2(0, 0)
        self.smoothing = 5.0  

        self.dead_zone_percent = dead_zone_percent
        self.dead_zone_x = self.width * self.dead_zone_percent
        self.dead_zone_y = self.height * self.dead_zone_percent
     
        self.dead_zone_rect = pygame.Rect(
            self.width // 2 - self.dead_zone_x // 2, 
            self.height // 2 - self.dead_zone_y // 2,
            self.dead_zone_x, 
            self.dead_zone_y
        )
    
    def update(self, target_rect, dt):
        """Updates the camera position based on the target (player) position.
        
        Args:
            target_rect: The player's rectangle to follow
            dt: Delta time for smooth movement
        """
        center_x = self.width // 2
        center_y = self.height // 2
        
        target_x = target_rect.centerx
        target_y = target_rect.centery
        
        screen_x = target_x - self.offset.x
        screen_y = target_y - self.offset.y
        
        target_offset_x = self.offset.x
        target_offset_y = self.offset.y
        
        if screen_x < self.dead_zone_rect.left:
            target_offset_x = target_x - self.dead_zone_rect.left
        elif screen_x > self.dead_zone_rect.right:
            target_offset_x = target_x - self.dead_zone_rect.right
            
        if screen_y < self.dead_zone_rect.top:
            target_offset_y = target_y - self.dead_zone_rect.top
        elif screen_y > self.dead_zone_rect.bottom:
            target_offset_y = target_y - self.dead_zone_rect.bottom
        
        self.offset.x = lerp(self.offset.x, target_offset_x, min(1.0, self.smoothing * dt))
        self.offset.y = lerp(self.offset.y, target_offset_y, min(1.0, self.smoothing * dt))
    
    def apply(self, entity):
        """Applies camera offset to an entity.
        
        Args:
            entity: An entity with a rect attribute
            
        Returns:
            A new rect with the camera offset applied
        """
        return pygame.Rect(
            entity.rect.x - int(self.offset.x),
            entity.rect.y - int(self.offset.y),
            entity.rect.width,
            entity.rect.height
        )
    
    def apply_rect(self, rect):
        """Applies camera offset to a rectangle.
        
        Args:
            rect: A pygame Rect
            
        Returns:
            A new rect with the camera offset applied
        """
        return pygame.Rect(
            rect.x - int(self.offset.x),
            rect.y - int(self.offset.y),
            rect.width,
            rect.height
        )
    
    def reset(self, center_position):
        """Resets the camera to center on a position.
        
        Args:
            center_position: (x, y) position to center on
        """
        self.offset.x = center_position[0] - self.width // 2
        self.offset.y = center_position[1] - self.height // 2
    
    def resize(self, new_width, new_height):
        """Adjusts the camera for window resizing.
        
        Args:
            new_width: New viewport width
            new_height: New viewport height
        """
        self.width = new_width
        self.height = new_height
        
        self.dead_zone_x = self.width * self.dead_zone_percent
        self.dead_zone_y = self.height * self.dead_zone_percent
        
        self.dead_zone_rect = pygame.Rect(
            self.width // 2 - self.dead_zone_x // 2, 
            self.height // 2 - self.dead_zone_y // 2,
            self.dead_zone_x, 
            self.dead_zone_y
        )
