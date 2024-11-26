import pygame
from pyvidplayer2 import Video,VideoPlayer
import time

import numpy as np

# pygame

pygame.init()

WIDTH, HEIGHT = 1920, 1080
 
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neurofeedback")

BG_COLOR = (0,0,0)

vid = VideoPlayer(Video("breaking_bad.mp4"), (0, 0, WIDTH, HEIGHT),)

while True:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            vid.close()
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
            key = pygame.key.name(event.key)
    
    pygame.time.wait(16)

    SCREEN.fill('black')

    vid.update()
    vid.draw(SCREEN)
    
    pygame.display.update()