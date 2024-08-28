import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import numpy as np 
import matplotlib.pyplot as plt
from scipy.signal import stft, butter, filtfilt, find_peaks, get_window
from scipy.fft import fft
from tkinter import filedialog

from typing import Optional

def plot_fft_stft_from_file(fname: Optional[str] = None,
                            file_path: Optional[str] = None,
                            output_path: Optional[str] = None,
                            window_type: Optional[str] = None,
                            smoothing: Optional[float] = 0,
                            threshold: Optional[float] = 0.005,
                            zero_padding: Optional[int] = None,
                            annotate_peaks: bool = True,
                            magnitude_scale: str = 'linear',
                            frequency_scale: str = 'log',
                            show_plot=True,
                            crop_beginning: Optional[int] = False):
    """
    Load accelerometer data from a numpy file, optionally filter, and plot both FFT and STFT.

    Parameters:
    -----------
    fname : str, optional
        Base name of the output plot file.
    file_path : str, optional
        Path to the numpy file containing accelerometer data.
    output_path : str, optional
        Path where the output plots will be saved.
    window_type : str, optional
        Type of window function to apply to the data before FFT and STFT.
    smoothing : float, optional
        Smoothing factor for the FFT plot. Default is 0 (no smoothing).
    threshold : float, optional
        Minimum height for peak detection in the FFT plot.
    zero_padding : int, optional
        Number of zeros to pad to the signal for FFT computation.
    annotate_peaks : bool, default=True
        Whether to annotate peaks in the FFT plot.
    magnitude_scale : str, default='linear'
        Scale for the magnitude axis in FFT ('linear' or 'log').
    frequency_scale : str, default='log'
        Scale for the frequency axis in FFT and STFT ('linear' or 'log').
    show_plot : bool, default=True
        Whether to display the plots after saving.
    crop_beginning : int, optional
        Crop the beginning of the data up to the highest peak.

    Returns:
    --------
    None
    """
    if file_path is None:
        file_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy")])

    if not file_path:
        print("No file selected.")
        return

    if output_path is None:
        output_dir = os.path.dirname(file_path)
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)

    data = np.load(file_path)
    timestamps = data[0]
    z_data = data[1]
    if crop_beginning: 
        highest_peak_index = np.argmax(z_data)  # find the index of the maximum value in z_data
        timestamps = timestamps[highest_peak_index:] # crop timestamps from the highest peak onward
        
        z_data = z_data[highest_peak_index:] # crop z_data from the highest peak onward
        timestamps = timestamps - timestamps[0] #normalize timestamps to start at 0 seconds, i.e. timestamps - timestamps[0]
        print(f"Data cropped until {timestamps[0]} seconds")
        print(z_data)
    
    fs = int(len(timestamps) / timestamps[-1])
    cutoff_freq = 200
    filtered_z_data = low_pass_filter(z_data, cutoff_freq, fs)
    filtered_data_path = os.path.join(output_dir, 'filtered_accelerometer_data.npy')
    np.save(filtered_data_path, np.vstack((timestamps, filtered_z_data)))

    # Plot without window
    plot_fft_stft(timestamps, z_data, output_dir, smoothing=smoothing, threshold=threshold,
                  window_type=None, zero_padding=zero_padding, annotate_peaks=annotate_peaks,
                  magnitude_scale=magnitude_scale, frequency_scale=frequency_scale, show_plot=show_plot)

    # Plot with specified window if provided
    if window_type:
        plot_fft_stft(timestamps, z_data, output_dir, fname, smoothing=smoothing, threshold=threshold,
                      window_type=window_type, zero_padding=zero_padding, annotate_peaks=annotate_peaks,
                      magnitude_scale=magnitude_scale, frequency_scale=frequency_scale, show_plot=show_plot)


def plot_fft_stft(timestamps: np.ndarray,
                  waveform: np.ndarray,
                  output_dir: str,
                  file_name: Optional[str] = None,
                  freq: Optional[int] = 44100,
                  ns: Optional[int] = 1024 * 2,
                  smoothing: Optional[float] = 0,
                  threshold: Optional[float] = 0.005,
                  show_plot: Optional[bool] = True,
                  window_type: Optional[str] = None,
                  zero_padding: Optional[int] = None,
                  annotate_peaks: bool = True,
                  magnitude_scale: str = 'linear',
                  frequency_scale: str = 'log'):
    """
    Plot the FFT and STFT of a given waveform, optionally applying windowing, zero padding, and peak annotation.

    Parameters:
    -----------
    timestamps : np.ndarray
        Array of timestamps corresponding to the waveform data.
    waveform : np.ndarray
        Array of waveform data (e.g., accelerometer data).
    output_dir : str
        Directory where the output plots will be saved.
    file_name : str, optional
        Base name for the output plot file.
    freq : int, optional
        Sampling frequency of the data. Default is 44100 Hz.
    ns : int, optional
        Number of samples per segment for STFT. Default is 2048.
    smoothing : float, optional
        Smoothing factor for the FFT plot. Default is 0 (no smoothing).
    threshold : float, optional
        Minimum height for peak detection in the FFT plot.
    show_plot : bool, optional
        Whether to display the plots after saving. Default is True.
    window_type : str, optional
        Type of window function to apply to the data before FFT and STFT.
    zero_padding : int, optional
        Number of zeros to pad to the signal for FFT computation.
    annotate_peaks : bool, default=True
        Whether to annotate peaks in the FFT plot.
    magnitude_scale : str, default='linear'
        Scale for the magnitude axis in FFT ('linear' or 'log').
    frequency_scale : str, default='log'
        Scale for the frequency axis in FFT and STFT ('linear' or 'log').

    Returns:
    --------
    None
    """
    
    freq = int((len(timestamps) - 2000) / timestamps[-2001])
    overlap = ns // 2

    if window_type:
        window = get_window(window_type, len(waveform))
        waveform_windowed = waveform * window
        label_suffix = f' with {window_type.capitalize()} Window'
    else:
        waveform_windowed = waveform
        label_suffix = ' (No Window)'

    # Apply zero padding if specified and valid
    original_length = len(waveform_windowed)
    if zero_padding and zero_padding > original_length:
        padded_length = zero_padding
        waveform_windowed = np.pad(waveform_windowed, (0, padded_length - original_length), 'constant')
    else:
        padded_length = original_length

    # Perform FFT
    Y = fft(waveform_windowed)
    f_fft = np.fft.fftfreq(padded_length, d=1 / freq)[:padded_length // 2]
    magnitude_spectrum = 2.0 / len(waveform_windowed) * np.abs(Y[:padded_length // 2])

    # Remove non-positive frequencies for log scale
    positive_freq_indices = f_fft > 0
    f_fft = f_fft[positive_freq_indices]
    magnitude_spectrum = magnitude_spectrum[positive_freq_indices]

    # Detect peaks before converting to log scale
    peaks, _ = find_peaks(magnitude_spectrum, height=threshold)

    # If magnitude scale is log, convert the magnitude spectrum
    if magnitude_scale == 'log':
        magnitude_spectrum = np.log10(magnitude_spectrum + 1e-10)  # Avoid log of zero or negative numbers

    fig, axs = plt.subplots(1, 2, figsize=(10, 5), dpi=150, gridspec_kw={"width_ratios": [2, 1]})

    axs[1].plot(magnitude_spectrum, f_fft, label=f'FFT{label_suffix}', color='blue', alpha=0.6)

    if annotate_peaks:
        for peak in peaks:
            peak_freq = f_fft[peak]
            axs[1].annotate(f'{peak_freq:.2f} Hz', xy=(magnitude_spectrum[peak], peak_freq),
                            xytext=(magnitude_spectrum[peak] * 1.1, peak_freq * 1.05),
                            arrowprops=dict(facecolor='black', arrowstyle='->'))
            axs[1].axhline(peak_freq, color='blue', linestyle='--', linewidth=0.7)

    horizontal_lines = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

    for line_freq in horizontal_lines:
        axs[1].axhline(line_freq, color='red', linestyle='-', linewidth=1.0)

    # Adjust Y-axis limits to avoid issues with logarithmic scale
    if frequency_scale == 'log' and np.any(f_fft <= 0):
        print("Skipping log scale on frequency axis due to non-positive frequency values.")
        axs[1].set_yscale('linear')
    else:
        axs[1].set_yscale(frequency_scale)
        axs[0].set_yscale(frequency_scale)

    axs[1].set_ylim((max(1, np.min(f_fft)), 500))
    axs[1].set_xlim(left=1e-10 if magnitude_scale == 'log' else 0)  # Handle log scale edge case
    axs[1].set_title(f'{"Smoothed" if smoothing > 0 else "Normal"} FFT{label_suffix}')
    axs[1].set_ylabel('Frequency [Hz]')

    # Apply the selected scale for the magnitude and frequency
    if magnitude_scale == 'log':
        axs[1].set_xscale('log')
    
    f, t, Zxx = stft(waveform, freq, noverlap=overlap, nperseg=ns, window='hann', nfft=ns * 2)
    
    axs[0].pcolormesh(t, f, np.abs(Zxx), shading='auto', cmap='viridis')
    if frequency_scale == 'log':
        print("Skipping log scale on STFT frequency axis due to non-positive frequency values.")
        axs[0].set_yscale('linear')
    else:
        axs[0].set_yscale(frequency_scale)
    axs[0].set_ylim((max(1, np.min(f[f > 0])), 500))
    axs[0].set_title(f'Short-time FFT (STFT){label_suffix}')
    axs[0].set_ylabel('Frequency [Hz]')
    axs[0].set_xlabel('Time [sec]')

    try:
        plt.tight_layout()
    except ValueError as e:
        print(f"Error during layout adjustment: {e}")

    if file_name is None:
        plt.savefig(os.path.join(output_dir, f'fft_stft_plot_{window_type if window_type else "no_window"}_smoothing_{smoothing}_zero_padding_{zero_padding}_magnitude_scale_{magnitude_scale}_frequency_scale_{frequency_scale}.png'))
    else:
        plt.savefig(os.path.join(output_dir, f'{file_name}_{window_type if window_type else "no_window"}_{smoothing}_zero_padding_{zero_padding}_magnitude_scale_{magnitude_scale}_frequency_scale_{frequency_scale}.png'))

    print(f"FFT and STFT plots saved in {output_dir}")
    if show_plot:
        plt.show()


def low_pass_filter(data: np.ndarray, cutoff_freq: float, fs: float, order: Optional[int] = 2) -> np.ndarray:
    """
    Apply a low-pass Butterworth filter to the input data.

    Parameters:
    -----------
    data : np.ndarray
        Input data to be filtered.
    cutoff_freq : float
        Cutoff frequency for the low-pass filter.
    fs : float
        Sampling frequency of the input data.
    order : int, optional
        Order of the Butterworth filter. Default is 2.

    Returns:
    --------
    filtered_data : np.ndarray
        The filtered output data.
    """
    nyquist = 0.5 * fs
    normal_cutoff = cutoff_freq / nyquist
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


if __name__ == "__main__":
    plot_fft_stft_from_file(file_path='/home/cslab/Desktop/Vibration-Tester-ADXL357-FFT-legacy/Example Recordings/tests_for_comparing_1st_nfreq/50cm_adxl/08-12_11-47-59_adxl6cmfromtip2cmID/accelerometer_data.npy',
                            smoothing=0, window_type='hann', zero_padding=4096, annotate_peaks=True, magnitude_scale='linear', frequency_scale='log', show_plot=True, crop_beginning=True)
