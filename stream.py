import pygame
import socket
import struct
import numpy as np

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neurofeedback")
BG_COLOR = (0, 0, 0)

# Socket setup
host = "192.168.137.1"  # Vervang met het IP-adres van de server-laptop
port = 5000
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Video simulatie of ander visueel feedback
running = True
brightness = 5

try:
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Ontvang data van server
        data = client_socket.recv(4)  # Ontvang één float (4 bytes)
        if not data:
            break

        # Decodeer ontvangen data
        sample_value = struct.unpack('f', data)[0]
        random_brightness = sample_value - 5

        # Bereken helderheid
        brightness += 0.01 * (random_brightness - brightness)
        brightness = max(0, min(brightness, 10))

        # Visualiseer helderheid met een kleurverandering
        SCREEN.fill((int(25.5 * brightness), 0, 0))  # Simpel voorbeeld met rode kleur
        pygame.display.update()
        pygame.time.delay(16)

except Exception as e:
    print(f"Error: {e}")
finally:
    client_socket.close()
    pygame.quit()
