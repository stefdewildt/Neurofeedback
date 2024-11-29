import pygame
from pyvidplayer2 import Video, VideoPlayer
import numpy as np
import random

# pygame initialiseren
pygame.init()
pygame.mixer.init()  # Voor geluid

clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neurofeedback")

BG_COLOR = (0, 0, 0)
video = Video("ted-ed.mp4")
vid = VideoPlayer(video, (0, 0, WIDTH, HEIGHT))

# Geluid
beep_sound = pygame.mixer.Sound("beep.mp3")  # Zorg dat je een "beep.wav"-bestand hebt
beep_sound.set_volume(0.5)  # Standaard volume van de pieptoon
video_volume = 1.0  # Beginvolume van de video
brightness = 1.0
target_brightness = 1.0
adjust_speed = 0.01  # Hoe snel helderheid verandert

running = True
last_adjust_time = 0  # Tijd van de laatste helderheidsaanpassing
is_beeping = False  # Huidige status van de pieptoon

while running:
    clock.tick(60)
    seconds = int((pygame.time.get_ticks() - start_ticks) / 1000)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Nieuwe doelwaarden instellen op een interval van 2 seconden
    if seconds - last_adjust_time >= 2:
        last_adjust_time = seconds
        random_value = random.randint(2, 7)  # Willekeurige waarde tussen 1 en 10
        print(f"Random value: {random_value}")

        # Helderheid aanpassen
        if random_value <= 5:
            target_brightness = max(0.1, brightness - 0.1)
        else:
            target_brightness = min(1.0, brightness + 0.1)

        print(f"Target brightness: {target_brightness}")

    # Geleidelijke aanpassing van helderheid
    if brightness < target_brightness:
        brightness = min(target_brightness, brightness + adjust_speed)
    elif brightness > target_brightness:
        brightness = max(target_brightness, brightness - adjust_speed)

    # Geluidsbeheer afhankelijk van helderheid
    if brightness < 0.3:
        if not is_beeping:
            is_beeping = True
            beep_sound.play(-1)  # Pieptoon in een lus afspelen
            video.set_volume(0.0)  # Zet het videovolume op 0
    else:
        if is_beeping:
            is_beeping = False
            beep_sound.stop()  # Stop de pieptoon
            video.set_volume(video_volume)  # Herstel het videovolume

    SCREEN.fill(BG_COLOR)

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