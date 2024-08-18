# initialization.py

import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
import sounddevice as sd
import matplotlib
matplotlib.use('TkAgg')  # Set the backend to TkAgg
import matplotlib.pyplot as plt
from scipy.io import wavfile
import pandas as pd
import time
import threading
import queue
from datetime import datetime
from scipy.signal import chirp, resample, stft
from scipy.fft import fft
from scipy.interpolate import interp1d
from mpl_toolkits.mplot3d import Axes3D
import smbus
import json


# I2C bus initialization
bus = smbus.SMBus(1)

sensitivity = 0.061 / 2
i = 0

# Define register addresses
LSM6DS3_ADDR = 0x6A
CTRL1_XL = 0x10
CTRL2_G = 0x11
CTRL3_C = 0x12
CTRL6_C = 0x15
CTRL8_XL = 0x17
OUTZ_L_XL = 0x2C
OUTZ_H_XL = 0x2D


def init_LSM6DS3():
    bus.write_byte_data(LSM6DS3_ADDR, CTRL1_XL, 0x80)  # 1.66 kHz, 4g, High-performance mode
    bus.write_byte_data(LSM6DS3_ADDR, CTRL2_G, 0x00)   # Gyroscope in power-down mode
    bus.write_byte_data(LSM6DS3_ADDR, CTRL3_C, 0x44)   # Enable I2C fast mode
    bus.write_byte_data(LSM6DS3_ADDR, CTRL6_C, 0x10)   # Enable accelerometer high-performance mode
    bus.write_byte_data(LSM6DS3_ADDR, CTRL8_XL, 0x09)  # Enable LPF2 and set cutoff to 400Hz

# Global variables for accelerometer data
z_axis_data = []  # List to store Z-axis accelerometer data
timestamps_data = []  # List to store timestamps
start_time = None  # Start time for data collection
last_time = None  # Last timestamp for data collection
running = False  # Flag to control the data collection thread

# Queue for passing data between threads
data_queue = queue.Queue()

# Lock for synchronizing access to data
data_lock = threading.Lock()

# Input file path for saving/loading inputs
input_file_path = "last_inputs.json"

# Function to save inputs to a file
def save_inputs(duration, start_freq, end_freq, notes):
    inputs = {
        "duration": duration,
        "start_freq": start_freq,
        "end_freq": end_freq,
        "notes": notes
    }
    with open("last_inputs.json", "w") as f:
        json.dump(inputs, f)

# Function to load inputs from a file
def load_inputs(duration_entry, start_freq_entry, end_freq_entry, notes_entry):
    if os.path.exists(input_file_path):
        with open(input_file_path, "r") as f:
            inputs = json.load(f)
            duration_entry.insert(0, inputs["duration"])
            start_freq_entry.insert(0, inputs["start_freq"])
            end_freq_entry.insert(0, inputs["end_freq"])
            notes_entry.insert(0, inputs["notes"])

# Function to read accelerometer data
def read_acc_data():
    global last_time
    try:
        # Read Z-axis data from the accelerometer
        z_l = bus.read_byte_data(LSM6DS3_ADDR, OUTZ_L_XL)
        z_h = bus.read_byte_data(LSM6DS3_ADDR, OUTZ_H_XL)
        z = (z_h << 8 | z_l)
        if z >= 32768:
            z -= 65536
        z_g = z * sensitivity / 1000  # Convert raw data to g

        # Calculate the current time and sampling rate
        current_time = time.time()
        if last_time is not None:
            interval = current_time - last_time
            sampling_rate = 1 / interval
        last_time = current_time
        elapsed_time = current_time - start_time

        with data_lock:

            z_axis_data.append(z_g)
            timestamps_data.append(elapsed_time)

            print(f"Z: {z_g:.3f}g, Time: {elapsed_time:.6f}s, "
                  f"Sampling Rate: {sampling_rate:.2f} Hz, len(z_axis_data):{len(z_axis_data)}")
    except Exception as e:
        print(f"Error: {e}")

# Thread function to continuously read data
def read_data_thread(duration):
    global start_time, last_time, running
    start_time = time.time()
    last_time = start_time
    running = True
    while running and (time.time() - start_time) < duration:
        read_acc_data()
    running = False
    # After reading is done, put the data in the queue
    data_queue.put((z_axis_data, timestamps_data))

# Function to generate sine waveform using chirp
def generate_sine_waveform(start_freq, end_freq, sweep_time, sample_rate=44100):
    t = np.linspace(0, sweep_time, int(sample_rate * sweep_time))
    waveform = chirp(t, f0=start_freq, f1=end_freq, t1=sweep_time, method='linear')
    return waveform, t
    
# Save the notes
def save_notes(notes, run_time, sweep_time, start_freq, end_freq):
    with open(os.path.join(run_time, f"notes{run_time}.txt"), 'w') as f:
        f.write("TEST RUN NOTES\n")
        f.write(f"{run_time}\n")
        f.write(f"Sweep Time: {sweep_time}s\n")
        f.write(f"Start Frequency: {start_freq}Hz\n")
        f.write(f"End Frequency: {end_freq}Hz\n")
        f.write("Wave Shape: Sine\n")
        f.write(f"User Notes: {notes}\n")

# Main function to run the initialization
def main():
    # Initialize the sensor
    init_LSM6DS3()

if __name__ == "__main__":
    main()
