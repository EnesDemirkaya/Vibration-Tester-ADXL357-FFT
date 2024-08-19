import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import json

import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
import sounddevice as sd
import threading
import queue
from scipy.io import wavfile
from scipy.signal import chirp

# Assuming these are part of initialization or another module you have
from initialization_adxl import (
     save_notes,
    read_data_thread, data_queue
)
def generate_sine_waveform(start_freq, end_freq, sweep_time, sample_rate=44100):
    t = np.linspace(0, sweep_time, int(sample_rate * sweep_time))
    waveform = chirp(t, f0=start_freq, f1=end_freq, t1=sweep_time, method='linear')
    return waveform, t
def save_inputs(duration, start_freq, end_freq, volume, notes):
    data = {
        'duration': duration,
        'start_freq': start_freq,
        'end_freq': end_freq,
        'volume': volume,
        'notes': notes
    }
    with open('inputs.json', 'w') as f:
        json.dump(data, f)


def load_inputs(duration_entry, start_freq_entry, end_freq_entry, volume_entry, notes_entry):
    if os.path.exists('inputs.json'):
        with open('inputs.json', 'r') as f:
            data = json.load(f)
            duration_entry.insert(0, data['duration'])
            start_freq_entry.insert(0, data['start_freq'])
            end_freq_entry.insert(0, data['end_freq'])
            volume_entry.insert(0, data.get('volume', 1))  # Default volume to 1 if not found
            notes_entry.insert(0, data['notes'])

def save_accelerometer_numpy(z_data, timestamps, run_time):
    np.save(os.path.join(run_time, 'accelerometer_data.npy'), np.array([timestamps, z_data]))

def load_accelerometer_data():
    file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy")])
    if not file_path:
        return None, None
    data = np.load(file_path)
    return data[0], data[1]

def save_data(timestamps_acc, waveform_acc, run_time, sweep=None, timestamps_sweep=None, waveform_sweep=None):
    save_accelerometer_numpy(waveform_acc, timestamps_acc, run_time)
    if sweep:
        np.save(os.path.join(run_time, 'sweep_data.npy'), np.array([timestamps_sweep, waveform_sweep]))
    np.save(os.path.join(run_time, 'combined_data.npy'), np.array([timestamps_acc, waveform_acc, timestamps_sweep, waveform_sweep]))

def play_and_record():
    try:
        duration = float(duration_entry.get())
        start_freq = float(start_freq_entry.get())
        end_freq = float(end_freq_entry.get())
        volume = float(volume_entry.get())
        notes = notes_entry.get()

        save_inputs(duration_entry.get(), start_freq_entry.get(), end_freq_entry.get(), volume_entry.get(), notes_entry.get())

    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all fields.")
        return

    run_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(run_time, exist_ok=True)
    
    sample_rate = 44100
    waveform, timestamps_sweep = generate_sine_waveform(start_freq, end_freq, duration, sample_rate)
    waveform = waveform * volume  # Apply volume control

    wavfile.write(os.path.join(run_time, 'sweep.wav'), sample_rate, waveform.astype(np.float32))

    thread = threading.Thread(target=read_data_thread, args=(duration,))
    thread.daemon = True
    thread.start()

    sd.play(waveform, samplerate=sample_rate)
    sd.wait()

    window.after(1000, lambda: check_queue_and_save(run_time, timestamps_sweep, waveform, notes, duration, start_freq, end_freq))

def check_queue_and_save(run_time, timestamps_sweep, waveform_sweep, notes, duration, start_freq, end_freq):
    try:
        data = data_queue.get_nowait()
    except queue.Empty:
        window.after(1000, lambda: check_queue_and_save(run_time, timestamps_sweep, waveform_sweep, notes, duration, start_freq, end_freq))
    else:
        save_data(*data, run_time, sweep=True, timestamps_sweep=timestamps_sweep, waveform_sweep=waveform_sweep)
        save_notes(notes, run_time, duration, start_freq, end_freq)

def load_and_process_npy():
    timestamps_acc, z_data = load_accelerometer_data()
    if timestamps_acc is None or z_data is None:
        messagebox.showerror("Error", "No file selected or file is empty.")
        return

    run_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(run_time, exist_ok=True)

    save_data(timestamps_acc, z_data, run_time)

# GUI Setup
window = tk.Tk()
window.title("Frequency Sweep Generator")
window.geometry("600x600")

tk.Label(window, text="Sweep Time (s):", font=("Helvetica", 14)).pack(pady=10)
duration_entry = tk.Entry(window, font=("Helvetica", 14))
duration_entry.pack(pady=10)

tk.Label(window, text="Start Frequency (Hz):", font=("Helvetica", 14)).pack(pady=10)
start_freq_entry = tk.Entry(window, font=("Helvetica", 14))
start_freq_entry.pack(pady=10)

tk.Label(window, text="End Frequency (Hz):", font=("Helvetica", 14)).pack(pady=10)
end_freq_entry = tk.Entry(window, font=("Helvetica", 14))
end_freq_entry.pack(pady=10)

tk.Label(window, text="Volume (0-1):", font=("Helvetica", 14)).pack(pady=10)
volume_entry = tk.Entry(window, font=("Helvetica", 14))
volume_entry.pack(pady=10)

tk.Label(window, text="Notes:", font=("Helvetica", 14)).pack(pady=10)
notes_entry = tk.Entry(window, font=("Helvetica", 14))
notes_entry.pack(pady=10)

load_numpy_button = tk.Button(window, text="Load and Process Numpy Data", command=load_and_process_npy)
load_numpy_button.pack(pady=20)

combined_button = tk.Button(window, text="Play and Record Sweep", command=play_and_record)
combined_button.pack(pady=20)

load_inputs(duration_entry, start_freq_entry, end_freq_entry, volume_entry, notes_entry)

window.mainloop()
