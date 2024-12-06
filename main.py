import pygame
from pyvidplayer2 import Video, VideoPlayer
import numpy as np
import random
from pylsl import StreamInlet, resolve_stream, StreamInfo, StreamOutlet
from scipy.fft import fft
from scipy import signal
import traceback
import matplotlib.pyplot as plt
from scipy.signal import welch
from scipy.integrate import simpson

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

#variables for bladiebla
low,high = 12,15
sf = 256
win = sf * 2

sample_9 = np.empty((0))
sample_17 = np.empty((0))
sample_18 = np.empty((0))
sample_19 = np.empty((0))

min_9, max_9 = 2.74, 8.3
min_17, max_17 = 0.67, 1.08
min_18, max_18 = 0.75, 1.16
min_19, max_19 = 0.98, 1.46


try:

    while running:
        clock.tick(60)
        seconds = int((pygame.time.get_ticks() - start_ticks) / 1000)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        sample, timestamp = inlet.pull_chunk()
        if len(sample)==0:
            continue
        sample=np.array(sample)
        # print(sample.shape)

        sample_9=np.append(sample_9, sample[:,8])
        sample_17=np.append(sample_17, sample[:,16])
        sample_18=np.append(sample_18, sample[:,17])
        sample_19=np.append(sample_19, sample[:,18])



        # Nieuwe doelwaarden instellen op een interval van 2 seconden
        #if secondmarker>=2:
        if len(sample_19)>=2*sf:
            # filter (band pass toevoegen), wss 1 tot 30, we willen 50 hz eruit hebben(lichtnet)
            freqs_9, psd_9 = signal.welch(sample_9, sf, nperseg=win)
            freqs_17, psd_17 = signal.welch(sample_17, sf, nperseg=win)
            freqs_18, psd_18 = signal.welch(sample_18, sf, nperseg=win)
            freqs_19, psd_19 = signal.welch(sample_19, sf, nperseg=win)
            idx_smr_9 = np.logical_and(freqs_9>= low, freqs_9<= high)
            idx_smr_17 = np.logical_and(freqs_17>= low, freqs_17<= high)
            idx_smr_18 = np.logical_and(freqs_18>= low, freqs_18<= high)
            idx_smr_19 = np.logical_and(freqs_19>= low, freqs_19<= high)
            # plt.figure(figsize=(7,4))
            # plt.plot(freqs_9,psd_9)
            # plt.fill_between(freqs_9, psd_9, where=idx_smr_9, color='skyblue')
            # #plt.xlim([0,100])
            # plt.ylim([0,psd_9.max()*1.1])
            # g=plt.figure()
            # [print(samp) for samp in sample_19]
            # plt.plot(sample_19)
            # plt.show()
            # plt.show()
            freq_res_9 = freqs_9[1]-freqs_9[0]
            smr_power_9 = simpson(psd_9[idx_smr_9], dx=freq_res_9)
            freq_res_17 = freqs_17[1]-freqs_17[0]
            smr_power_17 = simpson(psd_17[idx_smr_17], dx=freq_res_17)
            freq_res_18 = freqs_18[1]-freqs_18[0]
            smr_power_18 = simpson(psd_18[idx_smr_18], dx=freq_res_18)
            freq_res_19 = freqs_19[1]-freqs_19[0]
            smr_power_19 = simpson(psd_19[idx_smr_19], dx=freq_res_19)
            print(f'SMR power 9: {smr_power_9}\n')
            print(f'SMR power 17: {smr_power_17}\n')
            print(f'SMR power 18: {smr_power_18}\n')
            print(f'SMR power 19: {smr_power_19}\n')

            percentage_9 = ((smr_power_9 - min_9)/max_9)
            percentage_17 = ((smr_power_17 - min_17)/max_17)
            percentage_18 = ((smr_power_18 - min_18)/max_18)
            percentage_19 = ((smr_power_19 - min_19)/max_19)
            print(f'percentages: {percentage_9}, {percentage_17}, {percentage_18}, {percentage_19}')
            combined = (percentage_17+percentage_18+percentage_19+percentage_9)/4
            print(f'Combined scale: {combined}')


            sample_9 = np.empty((0))
            sample_17 = np.empty((0))
            sample_18 = np.empty((0))
            sample_19 = np.empty((0))
            # running = False
        pygame.time.wait(16)
        if seconds - last_adjust_time >= 2:
            last_adjust_time = seconds
            
            # Helderheid aanpassen
            if combined <= 5:
                target_brightness = max(0.1, brightness - 0.1)
            else:
                target_brightness = min(1.0, brightness + 0.1)
            print(f"Target brightness: {target_brightness}")

        print(combined)
        target_brightness = combined
        if brightness < target_brightness:
            brightness = min(target_brightness, brightness + adjust_speed)
        elif brightness > target_brightness:
            brightness = max(target_brightness, brightness - adjust_speed)

            # print(f"Target brightness: {target_brightness}")

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

except Exception as e:
    print(traceback.format_exc())
    print(f"Error: {e}");

vid.close()
pygame.quit()
exit()