#Play_Sweep_and_Record.py

import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import json
import numpy as np
from datetime import datetime
import sounddevice as sd
import threading




import queue
from scipy.io import wavfile
from scipy.signal import chirp
from tkinter import filedialog, Tk

from initialization_adxl import (
    save_notes,
    read_data_thread, data_queue
)

def generate_sine_waveform(start_freq, end_freq, sweep_time, sample_rate=44100):
    t = np.linspace(0, sweep_time, int(sample_rate * sweep_time))
    waveform = chirp(t, f0=start_freq, f1=end_freq, t1=sweep_time, method='linear')
    return waveform, t

def save_inputs(duration, start_freq, end_freq, volume, notes, filename):
    data = {
        'duration': duration,
        'start_freq': start_freq,
        'end_freq': end_freq,
        'volume': volume,
        'notes': notes,
        'filename': filename
    }
    with open('inputs.json', 'w') as f:
        json.dump(data, f)

def load_inputs():
    if os.path.exists('inputs.json'):
        with open('inputs.json', 'r') as f:
            return json.load(f)
    return {}

def get_input(prompt, previous_value=None):
    if previous_value:
        prompt = f"{prompt} [{previous_value}]: "
    else:
        prompt = f"{prompt}: "
    value = input(prompt).strip()
    return value if value else previous_value

def save_accelerometer_numpy(z_data, timestamps, run_time, filename):
    np.save(os.path.join(run_time, f'{filename}.npy'), np.array([timestamps, z_data]))

def load_accelerometer_data():
    # Using Tkinter's file dialog to select a file path
    root = Tk()
    root.withdraw()  # Hide the main window
    file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy")])
    root.destroy()  # Close the Tkinter window

    if not file_path or not os.path.exists(file_path):
        print("No file selected or file does not exist.")
        return None, None
    data = np.load(file_path)
    return data[0], data[1]

def save_data(timestamps_acc, waveform_acc, run_time, filename, sweep=False, timestamps_sweep=None, waveform_sweep=None):
    """Save data from the accelerometer and optionally the sweep waveform."""
    
    # Save the accelerometer data
    save_accelerometer_numpy(waveform_acc, timestamps_acc, run_time, filename)
    
    if sweep and timestamps_sweep is not None and waveform_sweep is not None:
        # Save the sweep data separately
        np.save(os.path.join(run_time, f'{filename}_sweep.npy'), np.array([timestamps_sweep, waveform_sweep]))

def play_and_record(duration=None, start_freq=None, end_freq=None, volume=None, notes=None, filename=None):
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

    check_queue_and_save(run_time, timestamps_sweep, waveform, notes, duration, start_freq, end_freq, filename)

def check_queue_and_save(run_time, timestamps_sweep, waveform_sweep, notes, duration, start_freq, end_freq, filename):
    try:
        data = data_queue.get_nowait()
    except queue.Empty:
        print("Waiting for data...")
        check_queue_and_save(run_time, timestamps_sweep, waveform_sweep, notes, duration, start_freq, end_freq, filename)
    else:
        save_data(*data, run_time, filename, sweep=True, timestamps_sweep=timestamps_sweep, waveform_sweep=waveform_sweep)
        save_notes(notes, run_time, duration, start_freq, end_freq)
        print(f"Data saved to {run_time}")



# Example of how to call the functions:
play_and_record()  # Will prompt for all missing information
