import pygame

def draw_fps(screen, clock, font, screen_width):
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
    pos = (screen_width - fps_text.get_width() - 10, 10)
    screen.blit(fps_text, pos)