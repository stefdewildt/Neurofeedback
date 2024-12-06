import time
import numpy as np
from pylsl import StreamInfo, StreamOutlet

# Parameters for the LSL stream
n_channels = 25  # Number of EEG channels
sampling_rate = 256  # Sampling rate in Hz
chunk_size = 32  # Number of samples per chunk
stream_name = "EventIDE_Signal_Stream"
stream_type = "EEG"

# Create LSL stream info and outlet
info = StreamInfo(stream_name, stream_type, n_channels, sampling_rate, 'float32', 'simulated_eeg_25_channels')
outlet = StreamOutlet(info)

# Generate synthetic EEG data
def generate_eeg_data():
    """Generates a chunk of synthetic EEG data with 25 channels."""
    time = np.linspace(0, chunk_size / sampling_rate, chunk_size, endpoint=False)
    
    # Generate signals for different frequency bands
    delta = np.sin(2 * np.pi * 3 * time)  # Delta band (3 Hz)
    theta = np.sin(2 * np.pi * 6 * time)  # Theta band (6 Hz)
    alpha = np.sin(2 * np.pi * 10 * time)  # Alpha band (10 Hz)
    beta = np.sin(2 * np.pi * 20 * time)  # Beta band (20 Hz)

    # Create a base pattern of EEG data for 4 bands
    bands = np.array([delta, theta, alpha, beta]).T  # Shape: (chunk_size, 4)
    
    # Repeat and trim to match the number of channels
    repeated_bands = np.tile(bands, (1, n_channels // 4 + 1))[:, :n_channels]
    
    # Add random noise to simulate variability
    noise = np.random.normal(0, 0.1, (chunk_size, n_channels))
    chunk = repeated_bands + noise
    return chunk

# Simulate streaming
print(f"Starting simulated EEG stream with {n_channels} channels...")
try:
    while True:
        chunk = generate_eeg_data()  # Generate a chunk of EEG data
        outlet.push_chunk(chunk.tolist())  # Push the chunk to the LSL stream
        time.sleep(chunk_size / sampling_rate)  # Sleep to simulate real-time streaming
except KeyboardInterrupt:
    print("\nSimulation stopped.")
