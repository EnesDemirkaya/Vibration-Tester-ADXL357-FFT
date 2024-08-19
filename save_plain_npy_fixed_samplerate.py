#save_plain_npy_fixed_samplerate.py

import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor do not delete
import time
import numpy as np
from datetime import datetime
import smbus2 as smbus

# I2C address
I2C_ADDRESS = 0x1D  # 0x1D for the ADXL357, SOMETIMES 0X53 depending on configuration
goal_sampling_rate = 4000  # Hz
# ADXL357 Register Addresses
REG_ZDATA3 = 0x0E
REG_ODR_FILTER = 0x28
REG_POWER_CTL = 0x2D  # Power Control register
REG_RESET = 0x2F      # Reset register

# Initialize the I2C bus
bus = smbus.SMBus(1)

def init_ADXL357():
    # Reset the device
    bus.write_byte_data(I2C_ADDRESS, REG_RESET, 0x52)  # Reset command
    time.sleep(0.1)  # Wait for the reset to complete
    
    # Set ODR to 4000 Hz, no filters applied
    bus.write_byte_data(I2C_ADDRESS, REG_ODR_FILTER, 0x00)
    # bus.write_byte_data(I2C_ADDRESS, REG_ODR_FILTER, 0x01) # 2000Hz

    
    # Set the device to measurement mode
    bus.write_byte_data(I2C_ADDRESS, REG_POWER_CTL, 0x06)  # Enable measurement mode

def read_accel_data():
    # Read 3 bytes for Z-axis
    z = bus.read_i2c_block_data(I2C_ADDRESS, REG_ZDATA3, 3)
    
    # Combine bytes and apply two's complement
    z_data = (z[0] << 12) | (z[1] << 4) | (z[2] >> 4)
    
    if z_data & (1 << 19): z_data -= (1 << 20)
    
    return z_data * 0.0000187

def save_accelerometer_numpy(z_data, timestamps, run_time):
    np.save(os.path.join(run_time, 'accelerometer_data.npy'), np.array([timestamps, z_data]))

def collect_accelerometer_data():
    # Global variables for accelerometer data
    z_axis_data = []
    timestamps_data = []
    intervals = []
    start_time = None
    last_time = None

    def read_acc_data():
        nonlocal last_time
        try:
            # Read data
            z = read_accel_data()

            # Calculate the current time and elapsed time
            current_time = time.time()
            if last_time is not None:
                interval = current_time - last_time
                intervals.append(interval)
                sampling_rate = 1 / interval
            else:
                interval = 0
                sampling_rate = 0
            last_time = current_time
            elapsed_time = current_time - start_time

            z_axis_data.append(z)
            timestamps_data.append(elapsed_time)

            print(f"Z: {z:.6f}, Time: {elapsed_time:.6f}s, "
                  f"Sampling Rate: {sampling_rate:.2f} Hz")
        except Exception as e:
            print(f"Error: {e}")

    try:
        with open('last_run.txt', 'r') as file:
            last_duration = float(file.readline().strip())
            last_custom_name = file.readline().strip()
    except:
        last_duration = 10.0  # Default duration
        last_custom_name = "default_name"

    duration = float(input(f"Enter the duration for data collection (in seconds) [{last_duration}]: ") or last_duration)
    custom_name = input(f"Enter a custom name to append to the folder [{last_custom_name}]: ") or last_custom_name
    start_time = time.time()  # Initialize start_time
    last_time = start_time  # Initialize last_time

    init_ADXL357()

    # Create directory for the current run
    run_time = datetime.now().strftime(f'%m-%d_%H-%M-%S_{custom_name}')
    os.makedirs(run_time, exist_ok=True)

    while (time.time() - start_time) < duration:
        loop_start_time = time.time()
        
        read_acc_data()

        # Calculate time spent in the loop and adjust accordingly
        loop_end_time = time.time()
        elapsed_loop_time = loop_end_time - loop_start_time
        if elapsed_loop_time < (1.0 / goal_sampling_rate):  # If the loop runs faster than desired sample rate
            while time.time() - loop_start_time < (1.0 / goal_sampling_rate):
                pass  # Busy-wait until the next sample time

    save_accelerometer_numpy(z_axis_data, timestamps_data, run_time)

    if intervals:
        sampling_rate_std = np.std([1 / interval for interval in intervals])
        print(f"Standard Deviation of Sampling Rate: {sampling_rate_std:.6f} Hz")

    print(f"Data saved to directory: {run_time}")

    with open('last_run.txt', 'w') as file:
        file.write(f"{duration}\n")
        file.write(f"{custom_name}\n")

if __name__ == "__main__":
    collect_accelerometer_data()
