import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.fft import fft, fftfreq
from scipy.optimize import curve_fit
import os
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def estimate_dominant_frequency(timestamps, signal):
    """
    Estimate the dominant frequency of the signal using FFT.
    
    Args:
        timestamps (numpy array): The timestamps of the signal.
        signal (numpy array): The signal data.
        
    Returns:
        float: The estimated dominant frequency in Hz.
    """
    dt = timestamps[1] - timestamps[0]
    N = len(signal)
    signal_fft = fft(signal)
    freqs = fftfreq(N, dt)
    positive_freqs = freqs[:N//2]
    fft_magnitude = np.abs(signal_fft)[:N//2]
    dominant_frequency = positive_freqs[np.argmax(fft_magnitude)]
    return dominant_frequency

def dynamic_peak_detection(accelerometer_data, timestamps, exclude_after_max_peak=3, exclude_last_n_peaks=3, min_prominence=0.1):
    """
    Detect peaks dynamically based on the frequency of the input signal.
    Only use the peaks that occur after the highest peak, excluding a few immediately after and excluding the last few peaks.

    Args:
        accelerometer_data (numpy array): The raw accelerometer data.
        timestamps (numpy array): Corresponding timestamps for the data.
        exclude_after_max_peak (int, optional): Number of peaks to exclude immediately after the maximum peak. Defaults to 3.
        exclude_last_n_peaks (int, optional): Number of peaks to exclude from the end. Defaults to 3.
        min_prominence (float, optional): Minimum prominence to filter peaks. Defaults to 0.1 * signal standard deviation.
        
    Returns:
        tuple: (peaks, peak_values, peak_times)
    """
    # Estimate the dominant frequency using FFT
    dominant_frequency = estimate_dominant_frequency(timestamps, accelerometer_data)
    expected_period = 1.0 / dominant_frequency
    min_distance = max(int(expected_period / (timestamps[1] - timestamps[0])), 1)  # Ensure min_distance is at least 1
    
    signal_std = np.std(accelerometer_data)
    min_prominence = min_prominence * signal_std
    min_height = 0.1 * np.max(accelerometer_data)
    
    # Detect peaks
    peaks, properties = find_peaks(accelerometer_data, prominence=min_prominence, distance=min_distance, height=min_height)
    
    # Find the index of the highest peak
    highest_peak_index = np.argmax(accelerometer_data[peaks])
    
    # Select peaks after the highest peak, excluding the first few after the highest peak
    filtered_peaks = peaks[highest_peak_index + 1 + exclude_after_max_peak:]
    
    # Exclude the last few peaks
    if exclude_last_n_peaks > 0 and len(filtered_peaks) > exclude_last_n_peaks:
        filtered_peaks = filtered_peaks[:-exclude_last_n_peaks]

    # Extract peak times and values
    peak_times = timestamps[filtered_peaks]
    peak_values = accelerometer_data[filtered_peaks]
    
    return filtered_peaks, peak_values, peak_times

def find_damping_ratio(file_path=None, show_plot=True, exclude_after_max_peak=3, exclude_last_n_peaks=3, min_prominence=0.1, min_distance=None):
    """
    Analyze accelerometer data from a selected numpy file or from the provided file path,
    fit it to an exponential decay curve, and save a plot of the results with relevant annotations.
    
    This function identifies peaks in the accelerometer data dynamically based on the input signal's frequency.
    Only peaks occurring after the highest peak are considered, with additional filtering to exclude
    the first few peaks after the highest and the last few peaks.

    Args:
        file_path (str, optional): The path to the numpy file. If not provided, a UI will prompt the user to select a file.
        show_plot (bool, optional): If True, displays the plot. Defaults to True.
        exclude_after_max_peak (int, optional): Number of peaks to exclude immediately after the maximum peak. Defaults to 3.
        exclude_last_n_peaks (int, optional): Number of peaks to exclude from the end. Defaults to 3.
        min_prominence (float, optional): Minimum prominence to filter peaks. Defaults to 0.1 * signal standard deviation.
        min_distance (int, optional): Minimum distance between peaks. If not provided, it's calculated from FFT.
        
    Returns:
        tuple: Returns a tuple containing:
            - damping_ratio (float or None): The calculated damping ratio (zeta) or None if fitting was not possible.
            - r_squared (float or None): The coefficient of determination (R²) for the curve fit or None if fitting was not possible.
            - omega_d (float or None): The damped natural frequency in Hz or None if fitting was not possible.
            - plot_file_path (str or None): The file path where the plot is saved or None if no plot was generated.
    """
    if file_path is None:
        os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

        # Open a file selector window
        root = Tk()
        root.withdraw()  # Hide the root window
        file_path = askopenfilename(title="Select the numpy array file", filetypes=[("Numpy files", "*.npy")])

        if not file_path: 
            print("No file selected")
            return None, None, None, None

    # Load the data from the selected file
    data = np.load(file_path)

    # Assuming data format: [timestamps, accelerometer_data]
    timestamps = data[0]
    accelerometer_data = data[1]

    # Estimate the dominant frequency using FFT
    dominant_frequency = estimate_dominant_frequency(timestamps, accelerometer_data)

    # Calculate min_distance based on the dominant frequency, if not provided
    if min_distance is None:
        expected_period = 1.0 / dominant_frequency
        min_distance = max(int(expected_period / (timestamps[1] - timestamps[0])), 1)

    # Find peaks dynamically
    peaks, peak_values, peak_times = dynamic_peak_detection(
        accelerometer_data, timestamps, 
        exclude_after_max_peak, exclude_last_n_peaks, 
        min_prominence=min_prominence
    )

    # Check if enough peaks were detected (at least 2 peaks are required for meaningful fitting)
    if len(peaks) < 2:
        print("Insufficient peaks detected for curve fitting. Please check the input data.")
        return None, None, None, None

    # Calculate omega d in Hz using counting method by number of peaks per second
    if peak_times[-1] != peak_times[0]:
        omega_d = len(peak_times) / (peak_times[-1] - peak_times[0])
    else:
        omega_d = None  # Avoid division by zero if all peak times are the same

    # Logarithmic Decrement Method
    def exponential_decay(t, A0, beta):
        return A0 * np.exp(-beta * t)

    # Initial guesses for the parameters
    initial_guess = [peak_values[0], 1.0]

    # Fit the peak values to the exponential decay function
    try:
        popt, _ = curve_fit(exponential_decay, peak_times, peak_values, p0=initial_guess)
    except (RuntimeError, TypeError) as e:
        print(f"Error during curve fitting: {e}")
        return None, None, None, None

    A0, beta = popt

    # Calculate the fitted curve for the peak times
    fitted_curve = exponential_decay(peak_times, A0, beta)

    # Calculate the damping ratio using the logarithmic decrement method
    zeta_ld = beta / (2 * np.pi * np.sqrt(1 - (beta / (2 * np.pi))**2))

    # Calculate R^2 (coefficient of determination)
    residuals = peak_values - fitted_curve
    ss_res = np.sum(residuals**2)
    ss_tot = np.sum((peak_values - np.mean(peak_values))**2)
    r_squared = 1 - (ss_res / ss_tot)

    # Plot the data and the fitted curve
    plt.figure(figsize=(10, 6))
    plt.plot(timestamps, accelerometer_data, 'b-', label='Data')
    plt.plot(peak_times, peak_values, 'ro', label='Peaks')
    plt.plot(peak_times, fitted_curve, 'r--', label='Fitted Curve')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.title('Accelerometer Data with Logarithmic Decrement Fit')
    plt.grid(True)

    # Annotate the plot with the fitted values and R^2
    textstr = '\n'.join((
        f'Initial Amplitude (A0): {A0:.4f}',
        f'Decay Rate (beta): {beta:.4f}',
        f'Damping Ratio (zeta): {zeta_ld:.4f}',
        f'omega_d: {omega_d:.4f}' if omega_d else 'omega_d: not computed',
        f'R^2: {r_squared:.4f}'    
    ))
    plt.gcf().text(1-0.4, 0.6, textstr, fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    # Save the plot to the same directory as the opened file with higher resolution
    plot_path = os.path.splitext(file_path)[0] + "_log_decay_plot"
    run_time = datetime.now().strftime(f'%m-%d_%H-%M-%S_')
    plot_file_path = plot_path + run_time + ".png"
    plt.savefig(plot_file_path, dpi=600)  # Set dpi to 600 for higher resolution

    print(f"Initial Amplitude (A0): {A0:.4f}")
    print(f"Decay Rate (beta): {beta:.4f}")
    print(f"Damping Ratio (zeta): {zeta_ld:.4f}")
    print(f"R^2: {r_squared:.4f}")
    print(f"Plot saved to: {plot_file_path}")
    print(f"omega_d: {omega_d:.4f}" if omega_d else "omega_d: not computed")

    # Show the plot if requested
    if show_plot:
        plt.show()

    # Always return the results
    return zeta_ld, r_squared, omega_d, plot_file_path

# Example usage:
results = find_damping_ratio(
    show_plot=True,
    exclude_after_max_peak=6,
    exclude_last_n_peaks=3,
    min_prominence=0.2  # Example: adjust prominence as needed
)
if results and all(v is not None for v in results[:3]):
    damping_ratio, r_squared, omega_d, plot_path = results
    print(f"Damping Ratio: {damping_ratio}, R²: {r_squared}, Omega_d: {omega_d}, Plot Path: {plot_path}")
else:
    print("Analysis could not be completed due to insufficient data.")
