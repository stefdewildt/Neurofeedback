# -*- coding: utf-8 -*-
"""
Created on Wed Nov 27 18:22:26 2024

@author: thoma
"""
# publisher.py
from pylsl import StreamInfo, StreamOutlet
import time
import random

# Create a stream info object for publishing data
info = StreamInfo('RandomIntegerStream', 'integer', 1, 10, 'int32', 'RandomIntegerStream')

# Create a StreamOutlet (publisher) to push data to the stream
outlet = StreamOutlet(info)

print("Publishing stream on localhost...")

# Push random data to the stream every 0.1 seconds
while True:
    random_value = random.randint(0, 10)  # Example random integer for EEG data simulation
    outlet.push_sample([random_value])  # Send sample to the stream
    print(f"Published: {random_value}")
    time.sleep(0.1)  # Wait for 100ms (to simulate 10 Hz EEG data)
