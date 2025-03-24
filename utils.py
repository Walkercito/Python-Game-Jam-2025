import pygame

def draw_fps(screen, clock, font, screen_width, show_fps=True):
    if not show_fps:
        return
        
    fps = clock.get_fps()
    fps_text = font.render(f"FPS: {int(fps)}", True, (255, 255, 255))
    pos = (screen_width - fps_text.get_width() - 10, 10)
    screen.blit(fps_text, pos)

def draw_progress_bar(screen, progress, rect):
    pygame.draw.rect(screen, (255, 255, 255), rect, 2)
    inner_rect = (
        rect[0] + 2, 
        rect[1] + 2, 
        (rect[2] - 4) * (progress / 100), 
        rect[3] - 4
    )
    pygame.draw.rect(screen, (0, 150, 255), inner_rect)