#Play_Sweep_and_Record.py

import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import json
import numpy as np
from datetime import datetime
import sounddevice as sd
import threading
from typing import Optional
import queue
from scipy.io import wavfile
from scipy.signal import chirp
import time
from tkinter import filedialog, Tk
import smbus2 as smbus

# I2C bus initialization
bus = smbus.SMBus(1)

# Define register addresses for ADXL357
I2C_ADDRESS = 0x1D  # 0x1D for the ADXL357, SOMETIMES 0X53 depending on configuration

# Define the measurement range (options: ±10g, ±20g, ±40g)
MEASUREMENT_RANGE = 10  # Change this value to 10, 20, or 40 for different ranges

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

def save_inputs(
        duration: float, 
        start_freq: float, 
        end_freq: float, 
        volume: float, 
        notes: str, 
        filename: str
    ) -> None:
    """
    Save session input parameters to a JSON file.

    Args:
        duration (float): Duration of the sine sweep.
        start_freq (float): Start frequency of the sine sweep.
        end_freq (float): End frequency of the sine sweep.
        volume (float): Volume level for the sine sweep.
        notes (str): Notes related to the session.
        filename (str): Filename for saving the data.
    """
    inputs = {
        "duration": duration,
        "start_freq": start_freq,
        "end_freq": end_freq,
        "volume": volume,
        "notes": notes,
        "filename": filename
    }
    with open(input_file_path, "w") as f:
        json.dump(inputs, f)

def save_notes(
        notes: str, 
        run_time: str, 
        duration: float, 
        start_freq: float, 
        end_freq: float
    ) -> None:
    """
    Save session notes to a JSON file.

    Args:
        notes (str): Notes related to the session.
        run_time (str): The timestamp when the session was run.
        duration (float): Duration of the sine sweep.
        start_freq (float): Start frequency of the sine sweep.
        end_freq (float): End frequency of the sine sweep.
    """
    notes_data = {
        "notes": notes,
        "duration": duration,
        "start_frequency": start_freq,
        "end_frequency": end_freq
    }
    with open(os.path.join(run_time, 'notes.json'), 'w') as f:
        json.dump(notes_data, f)

def generate_sine_waveform(
        start_freq: float, 
        end_freq: float, 
        sweep_time: float, 
        sample_rate: int = 44100
    ) -> tuple[np.ndarray, np.ndarray]:
    """
    Generate a linear sine sweep waveform.

    Args:
        start_freq (float): Start frequency of the sine sweep.
        end_freq (float): End frequency of the sine sweep.
        sweep_time (float): Duration of the sine sweep.
        sample_rate (int, optional): Sampling rate for the waveform. Defaults to 44100.

    Returns:
        tuple[np.ndarray, np.ndarray]: The generated waveform and its corresponding time array.
    """
    t = np.linspace(0, sweep_time, int(sample_rate * sweep_time))
    waveform = chirp(t, f0=start_freq, f1=end_freq, t1=sweep_time, method='linear')
    return waveform, t

def save_accelerometer_numpy(
        z_data: np.ndarray, 
        timestamps: np.ndarray, 
        run_time: str, 
        filename: str
    ) -> str:
    """
    Save accelerometer data to a numpy file.

    Args:
        z_data (np.ndarray): Z-axis accelerometer data.
        timestamps (np.ndarray): Timestamps corresponding to the Z-axis data.
        run_time (str): The timestamp when the session was run.
        filename (str): Filename for saving the data.

    Returns:
        str: The file path where the data was saved.
    """
    npy_file_path = os.path.join(run_time, f'{filename}.npy')
    np.save(npy_file_path, np.array([timestamps, z_data]))
    return npy_file_path

def init_ADXL357() -> None:
    """
    Initialize the ADXL357 accelerometer by resetting it, setting the ODR, and enabling measurement mode.
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
    
    # Enable measurement mode
    bus.write_byte_data(I2C_ADDRESS, REG_POWER_CTL, 0x06)

    print("ADXL357 initialized and set to measurement mode.")

def read_acc_data() -> None:
    """
    Read Z-axis data from the ADXL357 accelerometer, calculate the corresponding time, and store it.

    The function reads data from the accelerometer, calculates the acceleration in g, 
    and appends it to the global lists z_axis_data and timestamps_data.
    """
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

def read_data_thread(duration: float) -> None:
    """
    Start a thread that continuously reads accelerometer data for a specified duration.

    Args:
        duration (float): The duration for which to read data in seconds.
    """
    global start_time, last_time, running
    start_time = time.time()
    last_time = start_time
    running = True
    while running and (time.time() - start_time) < duration:
        read_acc_data()
    running = False
    # After reading is done, put the data in the queue
    data_queue.put((np.array(z_axis_data), np.array(timestamps_data)))

def check_queue_and_save(
        run_time: str,
        timestamps_sweep: Optional[np.ndarray],
        waveform_sweep: Optional[np.ndarray],
        notes: str,
        duration: float,
        start_freq: float,
        end_freq: float,
        filename: str
    ) -> str:
    """
    Check the queue for data, save the data when available, and return the file path.

    Args:
        run_time (str): The timestamp when the session was run.
        timestamps_sweep (Optional[np.ndarray]): Timestamps for the sweep waveform.
        waveform_sweep (Optional[np.ndarray]): Sweep waveform data.
        notes (str): Notes related to the session.
        duration (float): Duration of the sine sweep.
        start_freq (float): Start frequency of the sine sweep.
        end_freq (float): End frequency of the sine sweep.
        filename (str): Filename for saving the data.

    Returns:
        str: The file path where the accelerometer data was saved.
    """
    while True:
        try:
            data = data_queue.get_nowait()
        except queue.Empty:
            print("Waiting for data...")
            time.sleep(0.1)  # Sleep briefly to avoid busy-waiting
            continue
        else:
            if timestamps_sweep is not None and waveform_sweep is not None:
                acc_file_path = save_data(*data, run_time, filename, sweep=True, timestamps_sweep=timestamps_sweep, waveform_sweep=waveform_sweep)
            else:
                acc_file_path = save_data(*data, run_time, filename)
            
            save_notes(notes, run_time, duration, start_freq, end_freq)
            print(f"Data saved to {run_time}")
            return acc_file_path

def save_data(
        timestamps_acc: np.ndarray, 
        waveform_acc: np.ndarray, 
        run_time: str, 
        filename: str, 
        sweep: Optional[bool] = False, 
        timestamps_sweep: Optional[np.ndarray] = None, 
        waveform_sweep: Optional[np.ndarray] = None
    ) -> str:
    """
    Save data from the accelerometer and optionally the sweep waveform.

    Args:
        timestamps_acc (np.ndarray): Timestamps for the accelerometer data.
        waveform_acc (np.ndarray): Accelerometer data (Z-axis).
        run_time (str): The timestamp when the session was run.
        filename (str): Filename for saving the data.
        sweep (Optional[bool]): Flag indicating whether sweep data is included. Defaults to False.
        timestamps_sweep (Optional[np.ndarray]): Timestamps for the sweep waveform. Defaults to None.
        waveform_sweep (Optional[np.ndarray]): Sweep waveform data. Defaults to None.

    Returns:
        str: The file path where the accelerometer data was saved.
    """
    # Save the accelerometer data and return its file path
    acc_file_path = save_accelerometer_numpy(waveform_acc, timestamps_acc, run_time, filename)
    
    if sweep and timestamps_sweep is not None and waveform_sweep is not None:
        # Save the sweep data separately
        np.save(os.path.join(run_time, f'{filename}_sweep.npy'), np.array([timestamps_sweep, waveform_sweep]))
    
    return acc_file_path

def play_and_record(
        duration: Optional[float] = None, 
        start_freq: Optional[float] = None, 
        end_freq: Optional[float] = None, 
        volume: Optional[float] = None, 
        notes: Optional[str] = None, 
        filename: Optional[str] = None
    ) -> str:
    """
    Play a sine sweep, record accelerometer data, and save the data.

    Args:
        duration (Optional[float]): Duration of the sine sweep. Defaults to None.
        start_freq (Optional[float]): Start frequency of the sine sweep. Defaults to None.
        end_freq (Optional[float]): End frequency of the sine sweep. Defaults to None.
        volume (Optional[float]): Volume level for the sine sweep. Defaults to None.
        notes (Optional[str]): Notes related to the session. Defaults to None.
        filename (Optional[str]): Filename for saving the data. Defaults to None.

    Returns:
        str: The file path where the accelerometer data was saved.
    """
    previous_inputs = load_inputs()

    duration = duration or get_input("Sweep Time (s)", previous_inputs.get('duration'))
    start_freq = start_freq or get_input("Start Frequency (Hz)", previous_inputs.get('start_freq'))
    end_freq = end_freq or get_input("End Frequency (Hz)", previous_inputs.get('end_freq'))
    volume = volume or get_input("Volume (0-1)", previous_inputs.get('volume', '1'))
    notes = notes or get_input("Notes", previous_inputs.get('notes'))
    filename = filename or get_input("Filename for saved data", previous_inputs.get('filename', 'accelerometer_data'))

    save_inputs(duration, start_freq, end_freq, volume, notes, filename)

    run_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(run_time, exist_ok=True)
    
    sample_rate = 44100
    waveform, timestamps_sweep = generate_sine_waveform(float(start_freq), float(end_freq), float(duration), sample_rate)
    waveform = waveform * float(volume)  # Apply volume control

    wavfile.write(os.path.join(run_time, 'sweep.wav'), sample_rate, waveform.astype(np.float32))

    thread = threading.Thread(target=read_data_thread, args=(float(duration),))
    thread.daemon = True
    thread.start()

    sd.play(waveform, samplerate=sample_rate)
    sd.wait()

    acc_file_path = check_queue_and_save(run_time, timestamps_sweep, waveform, notes, float(duration), float(start_freq), float(end_freq), filename)
    
    return acc_file_path

def load_inputs() -> dict:
    """
    Load previously saved input parameters from a JSON file.

    Returns:
        dict: A dictionary of saved input parameters.
    """
    if os.path.exists(input_file_path):
        with open(input_file_path, "r") as f:
            return json.load(f)
    return {}

def get_input(prompt: str, previous_value: Optional[str] = None) -> str:
    """
    Prompt the user for input, using a previous value as the default if provided.

    Args:
        prompt (str): The prompt to display to the user.
        previous_value (Optional[str]): The previous value to use as the default. Defaults to None.

    Returns:
        str: The user's input, or the previous value if no input is provided.
    """
    if previous_value:
        prompt = f"{prompt} [{previous_value}]: "
    else:
        prompt = f"{prompt}: "
    value = input(prompt).strip()
    return value if value else previous_value

if __name__ == "__main__":
    init_ADXL357()
    filepath = play_and_record()  # Will prompt for all missing information
    print(f"Accelerometer data saved at: {filepath}")
