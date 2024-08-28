import os
os.environ['DISPLAY'] = ':0'  # to run the code from SSH but show on the monitor do not delete
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
REG_RANGE = 0x2C      # Range register for ADXL357

# Initialize the I2C bus
bus = smbus.SMBus(1)

def init_ADXL357(MEASUREMENT_RANGE):
    """
    Initializes the ADXL357 accelerometer by resetting the device, setting the output data rate (ODR),
    configuring the measurement range, and enabling measurement mode.

    Parameters:
    MEASUREMENT_RANGE (int): The measurement range in g (10, 20, or 40).
    """
    # Reset the device
    bus.write_byte_data(I2C_ADDRESS, REG_RESET, 0x52)  # Reset command
    time.sleep(0.1)  # Wait for the reset to complete
    
    # Set ODR to 4000 Hz, no filters applied
    bus.write_byte_data(I2C_ADDRESS, REG_ODR_FILTER, 0x00)

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

def read_accel_data(MEASUREMENT_RANGE):
    """
    Reads the Z-axis acceleration data from the ADXL357 accelerometer and converts it to g units.

    Parameters:
    MEASUREMENT_RANGE (int): The measurement range in g (10, 20, or 40).

    Returns:
    float: The Z-axis acceleration in g.
    """
    # Read 3 bytes for Z-axis
    z = bus.read_i2c_block_data(I2C_ADDRESS, REG_ZDATA3, 3)
    
    # Combine bytes and apply two's complement
    z_data = (z[0] << 12) | (z[1] << 4) | (z[2] >> 4)
    
    # Apply two's complement correction
    if z_data & (1 << 19):
        z_data -= (1 << 20)
    
    # Convert raw data to g units based on the measurement range
    if MEASUREMENT_RANGE == 10:
        z_g = z_data * 0.0000187  # Scale for 10g range
    elif MEASUREMENT_RANGE == 20:
        z_g = z_data * 0.0000187 * 2  # Scale for 20g range (double the 10g range)
    elif MEASUREMENT_RANGE == 40:
        z_g = z_data * 0.0000187 * 4  # Scale for 40g range (four times the 10g range)

    return z_g

def save_accelerometer_numpy(z_data, timestamps, run_time):
    """
    Saves the accelerometer data and timestamps to a numpy array file.

    Parameters:
    z_data (list): List of Z-axis acceleration data.
    timestamps (list): List of timestamps corresponding to the acceleration data.
    run_time (str): The directory name where the data will be saved.

    Returns:
    str: The file path of the saved numpy array.
    """
    np.save(os.path.join(run_time, 'accelerometer_data.npy'), np.array([timestamps, z_data]))
    return os.path.join(run_time, 'accelerometer_data.npy')

def collect_accelerometer_data(duration=None, custom_name=None, measurement_range=10):
    """
    Collects Z-axis accelerometer data for a specified duration and saves it to a numpy array.

    Parameters:
    duration (float, optional): The duration for data collection in seconds. If None, the user is prompted to input a value.
    custom_name (str, optional): A custom name to append to the directory where data is saved. If None, the user is prompted to input a value.
    measurement_range (int, optional): The measurement range in g (10, 20, or 40). Defaults to 10g.

    Returns:
    str: The file path of the saved numpy array.
    """
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
            z = read_accel_data(measurement_range)

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

    # Load last run settings if available
    try:
        with open('last_run.txt', 'r') as file:
            last_duration = float(file.readline().strip())
            last_custom_name = file.readline().strip()
    except:
        last_duration = 10.0  # Default duration
        last_custom_name = "default_name"

    # Set parameters if not provided
    if duration is None:
        duration = float(input(f"Enter the duration for data collection (in seconds) [{last_duration}]: ") or last_duration)
    if custom_name is None:
        custom_name = input(f"Enter a custom name to append to the folder [{last_custom_name}]: ") or last_custom_name
    if measurement_range is None:
        measurement_range = int(input("Enter the measurement range (10, 20, or 40): "))
    
    start_time = time.time()  # Initialize start_time
    last_time = start_time  # Initialize last_time

    init_ADXL357(measurement_range)

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

    # Save data and return the filepath
    npy_file_path = save_accelerometer_numpy(z_axis_data, timestamps_data, run_time)

    if intervals:
        sampling_rate_std = np.std([1 / interval for interval in intervals])
        print(f"Standard Deviation of Sampling Rate: {sampling_rate_std:.6f} Hz")

    print(f"Data saved to directory: {run_time}")

    with open('last_run.txt', 'w') as file:
        file.write(f"{duration}\n")
        file.write(f"{custom_name}\n")

    return npy_file_path

if __name__ == "__main__":
    filepath = collect_accelerometer_data()
    print(f"Numpy array saved at: {filepath}")
