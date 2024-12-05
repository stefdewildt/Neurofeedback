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
adjust_speed = 0.01  # Hoe snel helderheid verandert

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
        print(sample.shape)

        sample_9=np.append(sample_9, sample[:,8])
        sample_17=np.append(sample_17, sample[:,16])
        sample_18=np.append(sample_18, sample[:,17])
        sample_19=np.append(sample_19, sample[:,18])



        # Nieuwe doelwaarden instellen op een interval van 2 seconden
        #if secondmarker>=2:
        if len(sample_17)>=10*sf:
            # print(f'Sample: {sample_17}\n {sample_17.shape}\n')
            # fft = np.fft.fft(sample_17)
            # fftfreq = np.fft.fftfreq(len(sample_17))
            # f=plt.plot(abs(fft[0:int(len(fft)/2)]))
            # filter (band pass toevoegen), wss 1 tot 30, we willen 50 hz eruit hebben(lichtnet)
            freqs, psd = signal.welch(sample_17, sf, nperseg=win)
            idx_delta = np.logical_and(freqs>= low, freqs<= high)
            plt.figure(figsize=(7,4))
            plt.plot(freqs,psd)
            plt.fill_between(freqs, psd, where=idx_delta, color='skyblue')
            #plt.xlim([0,100])
            plt.ylim([0,psd.max()*1.1])
            g=plt.figure()
            [print(samp) for samp in sample_17]
            plt.plot(sample_17)
            plt.show()
            plt.show()
            freq_res = freqs[1]-freqs[0]
            delta_power = simpson(psd[idx_delta], dx=freq_res)
            print(f'Delta power: {delta_power}')

            sample_9 = np.empty((0))
            sample_17 = np.empty((0))
            sample_18 = np.empty((0))
            sample_19 = np.empty((0))
            running = False


            # Bereken FFT en vermogen
            # fft_results_1 = fft(samples_1)
            # fft_results_2 = fft(samples_2)
            # fft_results_3 = fft(samples_3)
            # power_spectrum = np.abs(fft_results[:len(selected_data) // 2]) ** 2  # Power spectrum

            # # Neem het gemiddelde vermogen als indicatie voor feedback
            # mean_power = np.mean(power_spectrum)
            # feedback_value = scale_power_to_feedback(mean_power, baseline_power)
            # print(f"Mean Power: {mean_power:.2f}, Feedback Value: {feedback_value:.2f}")

            # # Helderheid aanpassen op basis van feedback
            # target_brightness = feedback_value / 10.0
            # print(f"Target brightness: {target_brightness:.2f}")

            # last_adjust_time = seconds
            # samples_1 = []

            # Helderheid aanpassen
        if brightness < target_brightness:
            brightness = min(target_brightness, brightness + adjust_speed)
        elif brightness > target_brightness:
            brightness = max(target_brightness, brightness - adjust_speed)

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

except Exception as e:
    print(traceback.format_exc())
    print(f"Error: {e}");

vid.close()
pygame.quit()
exit()