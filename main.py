import pygame
from pyvidplayer2 import Video,VideoPlayer
import time

import numpy as np

# pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
 
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neurofeedback")

BG_COLOR = (0,0,0)

vid = VideoPlayer(Video("breaking_bad.mp4"), (0, 0, WIDTH, HEIGHT),)

# Brightness factor
# brightness = 1.0


running = True

while running:
    key = None
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            # if event.key == pygame.K_UP:
            #     brightness += 0.1 
            # if event.key == pygame.K_DOWN:
            #     brightness = max(0.1, brightness - 0.1)   
            pass      

    
    pygame.time.wait(16)

    SCREEN.fill(BG_COLOR)

    brightness = np.random.uniform(0, 4)

    # Draw the video frame onto a temporary surface
    temp_surface = pygame.Surface((WIDTH, HEIGHT))
    vid.update()
    vid.draw(temp_surface)

    # Access the pixel data of the temp_surface
    frame_array = pygame.surfarray.pixels3d(temp_surface)

    # Apply brightness adjustment
    adjusted_frame = np.clip(frame_array * brightness, 0, 255).astype('uint8')

    # Convert the adjusted frame back to a Pygame surface
    adjusted_surface = pygame.surfarray.make_surface(adjusted_frame)

    # Blit the adjusted surface onto the screen
    SCREEN.blit(adjusted_surface, (0, 0))
    
    pygame.display.update()

vid.close()
pygame.quit()
exit()