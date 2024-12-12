import pygame
from pyvidplayer2 import Video, VideoPlayer
import numpy as np
from pylsl import StreamInlet, resolve_stream
from scipy.signal import welch
from scipy.integrate import simpson
import threading
import time
import traceback

# pygame initialiseren
pygame.init()
pygame.mixer.init()  # Voor geluid

clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()

WIDTH, HEIGHT = 1900, 1000
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neurofeedback")

BG_COLOR = (0, 0, 0)
video = Video("ted-ed_3.mp4")
vid = VideoPlayer(video, (0, 0, WIDTH, HEIGHT))

# Geluid
beep_sound = pygame.mixer.Sound("beep.mp3")  # Zorg dat je een "beep.wav"-bestand hebt
beep_sound.set_volume(0.25)  # Standaard volume van de pieptoon
video_volume = 1.0  # Beginvolume van de video
brightness = 1.0
target_brightness = 1.0
combined = target_brightness
adjust_speed = 0.2  # Hoe snel helderheid verandert

running = True
last_adjust_time = 0  # Tijd van de laatste helderheidsaanpassing
is_beeping = False  # Huidige status van de pieptoon

streams = resolve_stream('name', 'EventIDE_Signal_Stream')  
baseline_power = 5.0  # Dit is de baseline van de schaal

for stream in streams:
    print(f"Stream Name: {stream.name()}, Type: {stream.type()}")
inlet = StreamInlet(streams[0])

def scale_power_to_feedback(power, baseline, scale_min=1, scale_max=10):
    """Schaal de power naar een schaal van 1 tot 10, met baseline als 5."""
    scaled_value = 5 + (power - baseline) * (scale_max - scale_min) / (baseline * 2)
    return max(scale_min, min(scale_max, scaled_value))

# Variables voor EEG-verwerking
low, high = 12, 15
sf = 256
win = sf * 2

sample_9 = np.empty((0))
sample_17 = np.empty((0))
sample_18 = np.empty((0))
sample_19 = np.empty((0))

min_9, max_9 = 4.97, 11.4
min_17, max_17 = 6.47, 10.31
min_18, max_18 = 4.97, 7.60
min_19, max_19 = 4.56, 8.05

def data_acquisition_thread():
    global sample_9, sample_17, sample_18, sample_19, running
    while running:
        sample, timestamp = inlet.pull_chunk()
        if len(sample) == 0:
            continue
        sample = np.array(sample)
        sample_9 = np.append(sample_9, sample[:, 8])
        sample_17 = np.append(sample_17, sample[:, 16])
        sample_18 = np.append(sample_18, sample[:, 17])
        sample_19 = np.append(sample_19, sample[:, 18])
        time.sleep(1 / sf)  # Zorg ervoor dat de thread de data-acquisitie synchroniseert

# Start een aparte thread voor het verzamelen van EEG-data
data_thread = threading.Thread(target=data_acquisition_thread)
data_thread.start()

try:
    while running:
        clock.tick(60)  # Houd de framerate op 60 FPS
        seconds = int((pygame.time.get_ticks() - start_ticks) / 1000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Verwerk EEG-gegevens elke 2 seconden
        if len(sample_19) >= 60 * sf:
            # Filter de frequenties met een bandpass
            freqs_9, psd_9 = welch(sample_9, sf, nperseg=win)
            freqs_17, psd_17 = welch(sample_17, sf, nperseg=win)
            freqs_18, psd_18 = welch(sample_18, sf, nperseg=win)
            freqs_19, psd_19 = welch(sample_19, sf, nperseg=win)

            idx_smr_9 = np.logical_and(freqs_9 >= low, freqs_9 <= high)
            idx_smr_17 = np.logical_and(freqs_17 >= low, freqs_17 <= high)
            idx_smr_18 = np.logical_and(freqs_18 >= low, freqs_18 <= high)
            idx_smr_19 = np.logical_and(freqs_19 >= low, freqs_19 <= high)

            # Bereken de SMR-power voor elke frequentie
            smr_power_9 = simpson(psd_9[idx_smr_9], dx=freqs_9[1] - freqs_9[0])
            smr_power_17 = simpson(psd_17[idx_smr_17], dx=freqs_17[1] - freqs_17[0])
            smr_power_18 = simpson(psd_18[idx_smr_18], dx=freqs_18[1] - freqs_18[0])
            smr_power_19 = simpson(psd_19[idx_smr_19], dx=freqs_19[1] - freqs_19[0])
            combined_smr = (smr_power_9+smr_power_19+smr_power_18+smr_power_17)/4
            running = False

            print(f'SMR power 9: {smr_power_9}\n')
            print(f'SMR power 17: {smr_power_17}\n')
            print(f'SMR power 18: {smr_power_18}\n')
            print(f'SMR power 19: {smr_power_19}\n')
            print(f'Combined SMR Power: {combined_smr}')

            percentage_9 = ((smr_power_9 - min_9) / max_9)
            percentage_17 = ((smr_power_17 - min_17) / max_17)
            percentage_18 = ((smr_power_18 - min_18) / max_18)
            percentage_19 = ((smr_power_19 - min_19) / max_19)

            combined = (percentage_17 + percentage_18 + percentage_19 + percentage_9) / 4
            print(f'Combined scale: {combined}')

            # Reset de samples voor de volgende iteratie
            sample_9 = np.empty((0))
            sample_17 = np.empty((0))
            sample_18 = np.empty((0))
            sample_19 = np.empty((0))

        # Update helderheid elke 2 seconden
        if seconds - last_adjust_time >= 2:
            last_adjust_time = seconds

            # Helderheid aanpassen
            if combined <= 0.5:
                target_brightness = max(0.3, brightness - 0.1)
            else:
                target_brightness = min(1.0, brightness + 0.1)

        # Geleidelijke aanpassing van helderheid
        if brightness < target_brightness:
            brightness = min(target_brightness, brightness + adjust_speed)
        elif brightness > target_brightness:
            brightness = max(target_brightness, brightness - adjust_speed)

        # Geluidsbeheer afhankelijk van helderheid
        if brightness < 0.5:
            if not is_beeping:
                is_beeping = True
                beep_sound.play(-1)  # Pieptoon in een lus afspelen
                video.set_volume(0.0)  # Zet het videovolume op 0
        else:
            if is_beeping:
                is_beeping = False
                beep_sound.stop()  # Stop de pieptoon
                video.set_volume(video_volume)  # Herstel het videovolume

        # Vul het scherm met de achtergrondkleur
        SCREEN.fill(BG_COLOR)

        # Teken het videobeeld op een tijdelijke surface
        temp_surface = pygame.Surface((WIDTH, HEIGHT))

        vid.update()
        vid.draw(temp_surface)

        # Verkrijg de pixeldata van de tijdelijke surface
        frame_array = pygame.surfarray.pixels3d(temp_surface)

        # Pas de helderheid aan
        adjusted_frame = np.clip(frame_array * brightness, 0, 255).astype('uint8')

        # Zet het aangepaste frame om naar een Pygame surface
        adjusted_surface = pygame.surfarray.make_surface(adjusted_frame)

        # Blit de aangepaste surface naar het scherm
        SCREEN.blit(adjusted_surface, (0, 0))

        pygame.display.update()

except Exception as e:
    print(traceback.format_exc())
    print(f"Error: {e}")

vid.close()
pygame.quit()
exit()