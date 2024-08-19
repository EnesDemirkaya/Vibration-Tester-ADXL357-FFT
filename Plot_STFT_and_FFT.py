#Plot_STFT_and_FFT.py

import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import os
import numpy as np 
import matplotlib.pyplot as plt
from scipy.signal import stft, butter, filtfilt, find_peaks
from scipy.fft import fft
from tkinter import filedialog

# This function processes the accelerometer data from a numpy file and plots the FFT and STFT
def plot_fft_stft_from_file(file_path=None, smoothing=0, threshold=0.005):
    """
    This function loads accelerometer data from a specified numpy (.npy) file, applies a low-pass filter,
    and then plots both the FFT (Fast Fourier Transform) and STFT (Short-Time Fourier Transform) of the signal.

    Parameters:
    - file_path: (str) Path to the numpy file containing the data. If None, a file dialog will be shown to select the file.
    - smoothing: (float) Cutoff frequency for the low-pass filter applied to the FFT result for smoothing.
    - threshold: (float) Minimum height of peaks to be detected in the FFT plot.
    """
    if file_path is None:
        # If no file path is provided, open a file dialog to let the user select a file
        file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy")])
    
    if not file_path:
        # If no file was selected, exit the function
        print("No file selected.")
        return

    # Determine the output directory based on the file path
    output_dir = os.path.dirname(file_path)
    os.makedirs(output_dir, exist_ok=True)  # Ensure that the directory exists

    # Load the data from the selected numpy file
    data = np.load(file_path)
    timestamps = data[0]  # First element is assumed to be timestamps
    z_data = data[1]  # Second element is the accelerometer data (z-axis)

    # Calculate the sampling frequency (fs) based on the timestamps
    fs = int(len(timestamps) / timestamps[-1])
    
    # Set the cutoff frequency for the low-pass filter (to remove high-frequency noise)
    cutoff_freq = 200

    # Apply a low-pass filter to the accelerometer data
    filtered_z_data = low_pass_filter(z_data, cutoff_freq, fs)

    # Save the filtered data to a new numpy file
    filtered_data_path = os.path.join(output_dir, 'filtered_accelerometer_data.npy')
    np.save(filtered_data_path, np.vstack((timestamps, filtered_z_data)))

    # Plot the FFT and STFT without smoothing
    plot_fft_stft(timestamps, z_data, output_dir, smoothing=0, threshold=threshold)
    
    # Plot the FFT and STFT with the specified smoothing
    plot_fft_stft(timestamps, z_data, output_dir, smoothing=smoothing, threshold=threshold)

# This function calculates and plots the FFT and STFT of the provided waveform
def plot_fft_stft(timestamps, waveform, output_dir, freq=44100, ns=1024*2, smoothing=0, threshold=0.005):
    """
    This function calculates and plots the FFT (Fast Fourier Transform) and STFT (Short-Time Fourier Transform)
    of a given waveform.

    Parameters:
    - timestamps: (array) Array of timestamps corresponding to the waveform.
    - waveform: (array) The waveform data to be analyzed.
    - output_dir: (str) Directory where the resulting plots will be saved.
    - freq: (int) Sampling frequency, used for FFT and STFT calculations.
    - ns: (int) Number of samples per segment for the STFT.
    - smoothing: (float) Cutoff frequency for the low-pass filter applied to the FFT result.
    - threshold: (float) Minimum height of peaks to be detected in the FFT plot.
    """
    # Estimate the sampling frequency based on the timestamps
    freq = int((len(timestamps)-2000)/ timestamps[-2001])
    print(freq)
    
    # Calculate the overlap for the STFT (50% overlap is common)
    overlap = ns // 2

    # Calculate the STFT of the waveform
    f, t, Zxx = stft(waveform, freq, noverlap=overlap, nperseg=ns, window='hann', nfft=ns*2)

    # Calculate the FFT of the waveform
    n = len(waveform)
    f_fft = np.fft.fftfreq(n, d=1/freq)
    Y = fft(waveform)
    magnitude_spectrum = 2.0 / n * np.abs(Y[:n // 2])

    if smoothing > 0:
        smoothed_magnitude_spectrum = low_pass_filter(magnitude_spectrum, smoothing, freq)
    else:
        smoothed_magnitude_spectrum = magnitude_spectrum

    peaks, _ = find_peaks(smoothed_magnitude_spectrum, height=threshold)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6), dpi=150, sharey=True, gridspec_kw={"width_ratios": [2, 1]})

    ax2.plot(smoothed_magnitude_spectrum, f_fft[:n // 2], label=f'Smoothed FFT (smoothing={smoothing})' if smoothing > 0 else 'Normal FFT', color='blue', alpha=0.6)
    
    if smoothing:
        for peak in peaks:
            peak_freq = f_fft[peak]
            ax2.annotate(f'{peak_freq:.2f} Hz', xy=(smoothed_magnitude_spectrum[peak], peak_freq),
                         xytext=(smoothed_magnitude_spectrum[peak]*0.8, peak_freq*1.05),
                         arrowprops=dict(facecolor='black', arrowstyle='->'))
            ax2.axhline(peak_freq, color='blue', linestyle='--', linewidth=0.7)

    # Uncomment the line corresponding to your use case and comment the others
    # horizontal_lines = [6, 37.3, 106.1, 210.6, 315.2, 419.7, 524.3, 628.8, 733.4, 838, 942.5, 1047.1] ##50cm
    # horizontal_lines = [8,79, 57.5,163.2, 324.8, 476.5, 628.1, 779.8, 931.4, 1083.1, 1234.7, 1386.4] ##40cm
    # horizontal_lines = [4.1,26.1,74.1,146.6,219.1,291.6,364.1,436.6,509.1,581.6,654.1,726.6] ##60cm
    # horizontal_lines = [14.9,99.9,285.7,571.6,855.4,1149.3,1433.1,1716.9,1990.7,2264.6,2538.4,2812.3] ##30cm
    horizontal_lines = [10,20,30,40,50,60,70,80,90,100] ##vib generator

    for line_freq in horizontal_lines:
        ax2.axhline(line_freq, color='red', linestyle='-', linewidth=1.0)

    ax2.set_ylim((1, 500))
    ax2.set_xlim((0.0001, 0.5))
    ax2.set_yscale('log')
    ax2.set_title(f'{"Smoothed" if smoothing > 0 else "Normal"} FFT')
    ax2.set_xlabel('Magnitude')

    ax1.pcolormesh(t, f, np.abs(Zxx), shading='auto', cmap='viridis')
    ax1.set_ylim((0, 500))
    ax1.set_yscale('log')
    ax1.set_title('Short-time FFT (STFT)')
    ax1.set_ylabel('Frequency [Hz]')
    ax1.set_xlabel('Time [sec]')

    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f'fft_stft_plot_smoothing_{smoothing}.png'))
    print(f"FFT and STFT plots saved in {output_dir}")
    plt.show()

# Function to apply a low-pass filter to data
def low_pass_filter(data, cutoff_freq, fs, order=2):
    """
    This function applies a low-pass filter to the input data to remove high-frequency noise.

    Parameters:
    - data: (array) The input data to be filtered.
    - cutoff_freq: (float) The cutoff frequency for the low-pass filter.
    - fs: (float) The sampling frequency of the data.
    - order: (int) The order of the filter (higher order = sharper cutoff).

    Returns:
    - filtered_data: (array) The filtered data.
    """
    nyquist = 0.5 * fs  # Nyquist frequency (half the sampling frequency)
    normal_cutoff = cutoff_freq / nyquist  # Normalize the cutoff frequency
    b, a = butter(order, normal_cutoff, btype='low', analog=False)  # Design the low-pass filter
    filtered_data = filtfilt(b, a, data)  # Apply the filter to the data
    return filtered_data

# Example usage of the main function
plot_fft_stft_from_file(smoothing=100)
