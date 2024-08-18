# main_app.py
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
import openpyxl

# Import functions and variables from initialization.py
from initialization import (
    save_inputs, load_inputs, read_data_thread, data_queue, data_lock,
    save_notes, z_axis_data, timestamps_data, read_acc_data, init_LSM6DS3, generate_sine_waveform
)


# Function to save accelerometer data as numpy array
def save_accelerometer_numpy(z_data, timestamps, run_time):
    np.save(os.path.join(run_time, 'accelerometer_data.npy'), np.array([timestamps, z_data]))

# Function to plot and save accelerometer data as PNG
def plot_accelerometer_data(z_data, timestamps, run_time):
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, z_data)
    plt.xlabel('Time (s)')
    plt.ylabel('Z-axis Acceleration (g)')
    plt.title('Z-axis Acceleration vs Time')
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(run_time, 'accelerometer_data.png'))
    plt.close()

# New function to load and plot data from numpy arrays
def load_and_plot_numpy():
    file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy")])
    if file_path:
        data = np.load(file_path)
        timestamps = data[0]
        z_data = data[1]
        run_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        os.makedirs(run_time, exist_ok=True)
        
        save_accelerometer_numpy(z_data, timestamps, run_time)
        plot_accelerometer_data(z_data, timestamps, run_time)
        plot_fft_stft(timestamps, z_data, run_time)
        plot_combined_graphs(timestamps, z_data, timestamps, z_data, run_time)
        plot_combined_waterfall(timestamps, z_data, timestamps, z_data, run_time)
        plot_combined_3d_waterfall(timestamps, z_data, z_data, run_time)

# Function to play frequency sweep and record accelerometer data simultaneously
def play_and_record():
    try:
        duration = duration_entry.get()
        start_freq = start_freq_entry.get()
        end_freq = end_freq_entry.get()
        notes = notes_entry.get()
        
        save_inputs(duration, start_freq, end_freq, notes)

        duration = float(duration)
        start_freq = float(start_freq)
        end_freq = float(end_freq)
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numerical values for all fields.")
        return

    # Create directory for the current run
    run_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    os.makedirs(run_time, exist_ok=True)
    
    sample_rate = 44100
    waveform, timestamps = generate_sine_waveform(start_freq, end_freq, duration, sample_rate)
    
    wavfile.write(os.path.join(run_time, 'sweep.wav'), sample_rate, waveform.astype(np.float32))
    
    # Start recording accelerometer data
    thread = threading.Thread(target=read_data_thread, args=(duration,))
    thread.daemon = True
    thread.start()
    
    # Play the sweep sound
    sd.play(waveform, samplerate=sample_rate)
    sd.wait()  # Wait until the sound has finished playing
    
    # After the thread is started, check the queue for data
    window.after(1000, lambda: check_queue_and_plot(run_time, timestamps, waveform, notes, duration, start_freq, end_freq))

# Function to check the queue for data, process it and plot
def check_queue_and_plot(run_time, timestamps_sweep, waveform_sweep, notes, duration, start_freq, end_freq):
    """
    Checks the queue for data and plots it if available.

    Args:
        run_time (str): The timestamp of the current run.
        timestamps_sweep (list): The timestamps of the sweep data.
        waveform_sweep (numpy.ndarray): The sweep waveform data.
        notes (str): The notes for the current run.
        duration (float): The duration of the sweep in seconds.
        start_freq (float): The starting frequency of the sweep in Hz.
        end_freq (float): The ending frequency of the sweep in Hz.

    Returns:
        None

    This function checks the data queue for data and processes it if available. If the queue is empty, it schedules itself to be called again after 1000 milliseconds. If data is available, it calls the `process_and_plot` function to process and plot the data.
    """
    try:
        data = data_queue.get_nowait()
        print("Data received from queue:", data)
    except queue.Empty:
        window.after(1000, lambda: check_queue_and_plot(run_time, timestamps_sweep, waveform_sweep, notes, duration, start_freq, end_freq))
    else:
        process_and_plot(run_time, timestamps_sweep, waveform_sweep, data, notes, duration, start_freq, end_freq)

# Function to process and plot accelerometer data along with sweep data
def process_and_plot(run_time, timestamps_sweep, waveform_sweep, data_acc, notes, duration, start_freq, end_freq):
    sample_rate = 44100
    z_data, timestamps_acc = data_acc
    
    new_waveform_acc = interpolate_and_save_wav(timestamps_acc, z_data, timestamps_sweep, run_time, sample_rate)
    save_accelerometer_numpy(z_data,timestamps_acc,run_time)
    save_data_excel(timestamps_acc,z_data,run_time)
    save_notes(notes, run_time, duration, start_freq, end_freq)

    # Plot the graphs for the sweep and accelerometer data
    plot_fft_stft(timestamps_acc, z_data, run_time)  # New plot function
    plot_combined_graphs(timestamps_sweep, waveform_sweep, timestamps_sweep, new_waveform_acc, run_time)
    plot_combined_waterfall(timestamps_sweep, waveform_sweep, timestamps_acc, z_data, run_time)
    plot_combined_3d_waterfall(timestamps_sweep, waveform_sweep, new_waveform_acc, run_time)
    

def interpolate_and_save_wav(timestamps_acc, z_data, timestamps_sweep, run_time, sample_rate=44100):
    # Interpolate the data
    interp_func = interp1d(timestamps_acc, z_data, kind='linear', fill_value="extrapolate")
    new_waveform_acc = interp_func(timestamps_sweep)
    
    scaled_waveform_acc = np.int16(new_waveform_acc / np.max(np.abs(new_waveform_acc)) * 32767)
    
    # Save accelerometer data as wav
    wavfile.write(os.path.join(run_time, 'accelerometer.wav'), sample_rate, scaled_waveform_acc)
    
    return new_waveform_acc


# Function to save data to Excel
def save_data_excel(timestamps, waveform, run_time,filename='acc'):
    import pandas as pd
    data = {'Timestamp': timestamps,  'Amplitude': waveform}
    df = pd.DataFrame(data)
    df.to_excel(os.path.join(run_time, f'frequency_data_{filename}.xlsx'), index=False)

# Function to plot graphs
def plot_graphs(timestamps, waveform, run_time):
    plt.figure(figsize=(12, 12))
    
    # Plot amplitude vs time
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, waveform)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Amplitude vs Time')
    
    # 3D plot of spectrogram
    fig = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Create spectrogram
    nfft = 8192  # Increase NFFT for better frequency resolution
    fs = 44100
    Pxx, freqs, bins, im = plt.specgram(waveform, NFFT=nfft, Fs=fs, noverlap=4096, pad_to=16384, cmap='viridis')

    # Limit frequencies to 500 Hz
    freqs_limit = freqs[freqs <= 500]
    Pxx_limit = Pxx[:len(freqs_limit)]

    # Meshgrid for 3D plotting
    X, Y = np.meshgrid(freqs_limit, bins)
    Z = 10 * np.log10(Pxx_limit.T)
    
    ax.plot_surface(X, Y, Z, cmap='viridis')
    ax.set_xlabel('Frequency (Hz)')
    ax.set_ylabel('Time (s)')
    ax.set_zlabel('Intensity (dB)')
    ax.set_title('3D Spectrogram')

    plt.tight_layout()
    plt.savefig(os.path.join(run_time, '3d_spectrogram.png'))
    plt.show()

# Function to create waterfall plot
def plot_waterfall(timestamps, waveform, run_time):
    plt.figure(figsize=(12, 6))
    
    nfft = 8192  # Increase NFFT for better frequency resolution
    fs = 44100
    Pxx, freqs, bins, im = plt.specgram(waveform, NFFT=nfft, Fs=fs, noverlap=4096, pad_to=16384, cmap='viridis')
    
    # Limit frequencies to 500 Hz
    freqs_limit = freqs[freqs <= 500]
    Pxx_limit = Pxx[:len(freqs_limit)]

    plt.pcolormesh(bins, freqs_limit, 10 * np.log10(Pxx_limit), shading='gouraud', cmap='viridis')
    plt.colorbar(label='Intensity [dB]')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim([0, 500])
    plt.title('Waterfall Plot')
    plt.savefig(os.path.join(run_time, 'waterfall_plot.png'))
    plt.show()

# Function to plot FFT and STFT


def plot_fft_stft(timestamps, waveform, run_time, freq=44100, ns=256*32):

    #find frequency from timestamps[]/len(timestamps)
    freq=int(len(timestamps)/timestamps[-1])
    print(freq)
    overlap = ns // 2

    # Calculate STFT
    f, t, Zxx = stft(waveform, freq, noverlap=overlap, nperseg=ns, window='hann')

    # Calculate FFT
    n = len(waveform)
    f_fft = np.fft.fftfreq(n, d=1/freq)
    Y = fft(waveform)
    magnitude_spectrum = 2.0/n * np.abs(Y[:n//2])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5), sharey=True, gridspec_kw={"width_ratios": [2, 1]})

    # Plot FFT
    ax2.fill_betweenx(f_fft[:n//2], 0, magnitude_spectrum, color='#440154', alpha=1)
    ax2.set_ylim((1, 500))
    ax2.set_xlim((0.0001, 0.1))
    ax2.set_xscale('log')  # Set x-axis to log scale
    ax2.set_yscale('log')  # Set y-axis to log scale

    ax2.set_title('Full-time FFT')
    ax2.set_xlabel('Magnitude')

    # Plot STFT
    ax1.pcolormesh(t, f, np.abs(Zxx), shading='auto', cmap='viridis')#, vmin=0, vmax=0.025
    ax1.set_ylim((0, 500))
    ax1.set_yscale('log')  # Set y-axis to log scale

    ax1.set_title('Short-time FFT')
    ax1.set_ylabel('Frequency [Hz]')
    ax1.set_xlabel('Time [sec]')
    
    plt.tight_layout()
    plt.savefig(os.path.join(run_time, 'fft_stft_plot.png'))
    plt.show()

# Function to plot combined graphs
def plot_combined_graphs(timestamps_sweep, waveform_sweep, timestamps_acc, waveform_acc, run_time):
    plt.figure(figsize=(12, 12))

    # Function to convert time to frequency
    def time_to_freq(time):
        start_freq = float(start_freq_entry.get())
        end_freq = float(end_freq_entry.get())
        duration = timestamps_sweep[-1]
        return start_freq + (end_freq - start_freq) * time / duration

    # Plot the sweep waveformj

    plt.subplot(3, 1, 1)
    plt.plot(timestamps_sweep, waveform_sweep)
    plt.xlabel('Time (s)')
    plt.ylabel('Sweep Amplitude')
    plt.title('Sweep Amplitude vs Time')

    # Add secondary x-axis for frequency
    ax = plt.gca()
    secax = ax.secondary_xaxis('top', functions=(time_to_freq, lambda x: (x - float(start_freq_entry.get())) / (float(end_freq_entry.get()) - float(start_freq_entry.get())) * timestamps_sweep[-1]))
    secax.set_xlabel('Frequency (Hz)')

    # Plot the accelerometer waveform
    plt.subplot(3, 1, 2)
    plt.plot(timestamps_acc, waveform_acc)
    plt.xlabel('Time (s)')
    plt.ylabel('Accelerometer Amplitude')
    plt.title('Accelerometer Amplitude vs Time')
    
    # Combined plot
    plt.subplot(3, 1, 3)
    plt.plot(timestamps_sweep, waveform_sweep, label='Sweep')
    plt.plot(timestamps_acc, waveform_acc, label='Accelerometer', alpha=0.7)
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Combined Amplitude vs Time')
    plt.legend()
    
    # Add secondary x-axis for frequency
    ax = plt.gca()
    secax = ax.secondary_xaxis('top', functions=(time_to_freq, lambda x: (x - float(start_freq_entry.get())) / (float(end_freq_entry.get()) - float(start_freq_entry.get())) * timestamps_sweep[-1]))
    secax.set_xlabel('Frequency (Hz)')

    plt.tight_layout()
    plt.savefig(os.path.join(run_time, 'combined_plot.png'))
    plt.show()

# Function to create combined waterfall plot
def plot_combined_waterfall(timestamps_sweep, waveform_sweep, timestamps_acc, waveform_acc, run_time):
    plt.figure(figsize=(12, 12))

    # Waterfall plot for the sweep waveform
    plt.subplot(2, 1, 1)
    nfft = 8192  # Increase NFFT for better frequency resolution
    fs = 44100
    Pxx_sweep, freqs_sweep, bins_sweep, im_sweep = plt.specgram(waveform_sweep, NFFT=nfft, Fs=fs, noverlap=4096, pad_to=16384, cmap='viridis')
    freqs_sweep_limit = freqs_sweep[freqs_sweep <= 500]
    Pxx_sweep_limit = Pxx_sweep[:len(freqs_sweep_limit)]
    plt.pcolormesh(bins_sweep, freqs_sweep_limit, 10 * np.log10(Pxx_sweep_limit), shading='gouraud', cmap='viridis')
    plt.colorbar(label='Intensity [dB]')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim([0, 500])
    plt.title('Waterfall Plot - Sweep')

    # Waterfall plot for the accelerometer waveform
    plt.subplot(2, 1, 2)
    Pxx_acc, freqs_acc, bins_acc, im_acc = plt.specgram(waveform_acc, NFFT=nfft, Fs=fs, noverlap=4096, pad_to=16384, cmap='viridis')
    freqs_acc_limit = freqs_acc[freqs_acc <= 500]
    Pxx_acc_limit = Pxx_acc[:len(freqs_acc_limit)]
    plt.pcolormesh(bins_acc, freqs_acc_limit, 10 * np.log10(Pxx_acc_limit), shading='gouraud', cmap='viridis')
    plt.colorbar(label='Intensity [dB]')
    plt.xlabel('Time (s)')
    plt.ylabel('Frequency (Hz)')
    plt.ylim([0, 500])
    plt.title('Waterfall Plot - Accelerometer')

    plt.tight_layout()
    plt.savefig(os.path.join(run_time, 'combined_waterfall_plot.png'))
    plt.show()


# Function to plot combined 3D waterfall plot
def plot_combined_3d_waterfall(timestamps_sweep, waveform_sweep, waveform_acc, run_time):
    fig = plt.figure(figsize=(12, 12))

    # 3D waterfall plot for the sweep waveform
    ax1 = fig.add_subplot(211, projection='3d')
    nfft = 8192  # Increase NFFT for better frequency resolution
    fs = 44100
    Pxx_sweep, freqs_sweep, bins_sweep, im_sweep = plt.specgram(waveform_sweep, NFFT=nfft, Fs=fs, noverlap=4096, pad_to=16384, cmap='viridis')
    freqs_sweep_limit = freqs_sweep[freqs_sweep <= 500]
    Pxx_sweep_limit = Pxx_sweep[:len(freqs_sweep_limit)]
    X_sweep, Y_sweep = np.meshgrid(bins_sweep, freqs_sweep_limit)
    Z_sweep = 10 * np.log10(Pxx_sweep_limit)
    ax1.plot_surface(X_sweep, Y_sweep, Z_sweep, cmap='viridis')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('Frequency (Hz)')
    ax1.set_zlabel('Intensity (dB)')
    ax1.set_title('3D Waterfall Plot - Sweep')

    # 3D waterfall plot for the accelerometer waveform
    ax2 = fig.add_subplot(212, projection='3d')
    Pxx_acc, freqs_acc, bins_acc, im_acc = plt.specgram(waveform_acc, NFFT=nfft, Fs=fs, noverlap=4096, pad_to=16384, cmap='viridis')
    freqs_acc_limit = freqs_acc[freqs_acc <= 500]
    Pxx_acc_limit = Pxx_acc[:len(freqs_acc_limit)]
    X_acc, Y_acc = np.meshgrid(bins_acc, freqs_acc_limit)
    Z_acc = 10 * np.log10(Pxx_acc_limit)
    ax2.plot_surface(X_acc, Y_acc, Z_acc, cmap='viridis')
    ax2.set_xlabel('Time (s)')
    ax2.set_ylabel('Frequency (Hz)')
    ax2.set_zlabel('Intensity (dB)')
    ax2.set_title('3D Waterfall Plot - Accelerometer')

    plt.tight_layout()
    plt.savefig(os.path.join(run_time, 'combined_3d_waterfall_plot.png'))
    plt.show()


# Function to load .wav file and plot its graphs
def load_wav_file():
    file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
    if file_path:
        sample_rate, waveform = wavfile.read(file_path)
        timestamps = np.linspace(0, len(waveform) / sample_rate, num=len(waveform))
        frequencies = np.linspace(0, sample_rate / 2, num=len(timestamps))  # This is a placeholder
        run_time=datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        # Plot the graphs for the loaded .wav file
        plot_graphs(timestamps, waveform, run_time)
        plot_fft_stft(timestamps,waveform,run_time,sampling_rate = 44100)
        plot_waterfall(timestamps, waveform, run_time)

# Create the main window
window = tk.Tk()
window.title("Frequency Sweep Generator")
window.geometry("600x600")

# Define common style for better touch compatibility
style = ttk.Style()
style.configure("TButton", font=("Helvetica", 14), padding=10)
style.configure("TLabel", font=("Helvetica", 14))
style.configure("TEntry", font=("Helvetica", 14), padding=10)

# Add input fields and labels with padding for touch compatibility
tk.Label(window, text="Sweep Time (s):", font=("Helvetica", 14)).pack(pady=10)
duration_entry = tk.Entry(window, font=("Helvetica", 14))
duration_entry.pack(pady=10)

tk.Label(window, text="Start Frequency (Hz):", font=("Helvetica", 14)).pack(pady=10)
start_freq_entry = tk.Entry(window, font=("Helvetica", 14))
start_freq_entry.pack(pady=10)

tk.Label(window, text="End Frequency (Hz):", font=("Helvetica", 14)).pack(pady=10)
end_freq_entry = tk.Entry(window, font=("Helvetica", 14))
end_freq_entry.pack(pady=10)

tk.Label(window, text="Notes:", font=("Helvetica", 14)).pack(pady=10)
notes_entry = tk.Entry(window, font=("Helvetica", 14))
notes_entry.pack(pady=10)

load_wav_button = ttk.Button(window, text="Load and Plot WAV File", command=load_wav_file)
load_wav_button.pack(pady=20)

load_numpy_button = ttk.Button(window, text="Load and Plot Numpy Data", command=load_and_plot_numpy)
load_numpy_button.pack(pady=20)

combined_button = ttk.Button(window, text="Play and Record Sweep", command=play_and_record)
combined_button.pack(pady=20)

# Initialize the sensor
#init_LSM6DS3()

# Load inputs from the file
load_inputs(duration_entry, start_freq_entry, end_freq_entry, notes_entry)

# Run the application
window.mainloop()
