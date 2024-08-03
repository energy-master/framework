import pygame
import os
import time
import random

pygame.font.init()

WIDTH, HEIGHT = 750, 750
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MARLIN Ident GAME Visualiser")


def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    main_font = pygame.font.SysFont("comicsans", 40)
    
    def redraw_window():
        # Initializing RGB Color
        color = (0, 0, 255)
        # Changing surface color
        WIN.fill(color)
        # pygame.display.flip()
        
        name_label_surface = main_font.render(f'MARLIN Ident', 1, (255,0,0))
        WIN.blit(name_label_surface,(10,10))
        
        pygame.display.update()
        
        
        
    while run:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
    
main()