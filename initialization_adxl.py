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
import smbus2 as smbus
import json

# I2C bus initialization
bus = smbus.SMBus(1)

# Define register addresses for ADXL357
I2C_ADDRESS = 0x1D  # 0x1D for the ADXL357, SOMETIMES 0X53 depending on configuration

# Define the measurement range (options: ±10g, ±20g, ±40g)
MEASUREMENT_RANGE = 40  # Change this value to 10, 20, or 40 for different ranges

# ADXL357 Register Addresses
REG_ZDATA3 = 0x0E
REG_ODR_FILTER = 0x28
REG_POWER_CTL = 0x2D  # Power Control register
REG_RESET = 0x2F      # Reset register
REG_RANGE = 0x2C      # Range register for ADXL357

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
def save_notes(notes, run_time, duration, start_freq, end_freq):
    """Save session notes to a JSON file."""
    notes_data = {
        "notes": notes,
        "duration": duration,
        "start_frequency": start_freq,
        "end_frequency": end_freq
    }
    with open(os.path.join(run_time, 'notes.json'), 'w') as f:
        json.dump(notes_data, f)

# Function to load inputs from a file
def load_inputs(duration_entry, start_freq_entry, end_freq_entry, notes_entry):
    if os.path.exists(input_file_path):
        with open(input_file_path, "r") as f:
            inputs = json.load(f)
            duration_entry.insert(0, inputs["duration"])
            start_freq_entry.insert(0, inputs["start_freq"])
            end_freq_entry.insert(0, inputs["end_freq"])
            notes_entry.insert(0, inputs["notes"])

def init_ADXL357():
    """Initialize the ADXL357 accelerometer."""
    # Reset the device
    bus.write_byte_data(I2C_ADDRESS, REG_RESET, 0x52)  # Reset command
    time.sleep(0.1)  # Wait for the reset to complete
    
    # Set ODR to 4000 Hz, no filters applied
    bus.write_byte_data(I2C_ADDRESS, REG_ODR_FILTER, 0x00)
    
    # Set the device to measurement mode
    
    # Set the measurement range
    if MEASUREMENT_RANGE == 10:
        bus.write_byte_data(I2C_ADDRESS, REG_RANGE, 0x01)  # ±10g
    elif MEASUREMENT_RANGE == 20:
        bus.write_byte_data(I2C_ADDRESS, REG_RANGE, 0x02)  # ±20g
    elif MEASUREMENT_RANGE == 40:
        bus.write_byte_data(I2C_ADDRESS, REG_RANGE, 0x03)  # ±40g
    else:
        raise ValueError("Invalid measurement range specified. Use 10, 20, or 40.")
    bus.write_byte_data(I2C_ADDRESS, REG_POWER_CTL, 0x06)  # Enable measurement mode


    print("ADXL357 initialized and set to measurement mode.")

def read_acc_data():
    global last_time
    try:
        # Read Z-axis data from the accelerometer
        z = bus.read_i2c_block_data(I2C_ADDRESS, REG_ZDATA3, 3)
    
        # Combine bytes and apply two's complement
        z_data = (z[0] << 12) | (z[1] << 4) | (z[2] >> 4)
    
        if z_data & (1 << 19):
            z_data -= (1 << 20)
    
        # Adjust the scaling factor based on the range
        if MEASUREMENT_RANGE == 10:
            z_g = z_data * 0.0000187  # Scale for 10g range
        elif MEASUREMENT_RANGE == 20:
            z_g = z_data * 0.0000187 * 2  # Scale for 20g range (double the 10g range)
        elif MEASUREMENT_RANGE == 40:
            z_g = z_data * 0.0000187 * 4  # Scale for 40g range (four times the 10g range)
    
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

# Main function to run the initialization
def main():
    # Initialize the sensor
    init_ADXL357()

if __name__ == "__main__":
    main()
