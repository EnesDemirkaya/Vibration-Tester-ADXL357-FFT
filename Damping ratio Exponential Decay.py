import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import os
# main_app.py
import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def find_damping_ratio(file_path=None):
    """
    Analyze accelerometer data from a selected numpy file or from the provided file path,
    fit it to an exponential decay curve, and save a plot of the results with relevant annotations.

    Args:
        file_path (str): The path to the numpy file. If not provided, a UI will prompt the user to select a file.

    Returns:
        None
    """
    if file_path is None:
        os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

        # Open a file selector window
        root = Tk()
        root.withdraw()  # Hide the root window
        file_path = askopenfilename(title="Select the numpy array file", filetypes=[("Numpy files", "*.npy")])

        if not file_path: 
            print("No file selected")
            return

    # Load the data from the selected file
    data = np.load(file_path)

    # Assuming data format: [timestamps, accelerometer_data]
    timestamps = data[0]
    accelerometer_data = data[1]

    max_acc = max(accelerometer_data)

    # Find the peaks in the accelerometer data with specified parameters
    if 3.98 < max_acc < 4.01 or 1.97 < max_acc < 2.02:
        peaks, _ = find_peaks(accelerometer_data, distance=500, height=(0.01, max_acc - 0.01), prominence=0.2)
    else:
        peaks, _ = find_peaks(accelerometer_data, distance=500, height=0.01, prominence=0.2)

    # Find the index of the maximum peak
    max_peak_index = np.argmax(accelerometer_data[peaks])

    # Remove peaks that are smaller than the maximum peak (i.e., have a smaller x-location)
    peaks = [peak for peak in peaks if peak > peaks[max_peak_index]]

    # Remove the first and last peaks
    if len(peaks) > 2:
        peaks = peaks[2:-4]

    # Extract peak times and values
    peak_times = timestamps[peaks]
    peak_values = accelerometer_data[peaks]

    # Calculate omega d in Hz using counting method by number of peaks per second
    omega_d = len(peak_times) / (peak_times[-1] - peak_times[0])

    # Logarithmic Decrement Method
    def exponential_decay(t, A0, beta):
        return A0 * np.exp(-beta * t)

    # Initial guesses for the parameters
    initial_guess = [peak_values[0], 1.0]

    # Fit the peak values to the exponential decay function
    popt, _ = curve_fit(exponential_decay, peak_times, peak_values, p0=initial_guess)

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
        f'omega_d: {omega_d:.4f}',
        f'R^2: {r_squared:.4f}'    
    ))
    plt.gcf().text(1-0.4, 0.6, textstr, fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    # Save the plot to the same directory as the opened file with higher resolution
    plot_path = os.path.splitext(file_path)[0] + "_log_decay_plot"
    run_time = datetime.now().strftime(f'%m-%d_%H-%M-%S_')

    plt.savefig(plot_path + run_time + ".png", dpi=600)  # Set dpi to 600 for higher resolution
    print(f"Initial Amplitude (A0): {A0:.4f}")
    print(f"Decay Rate (beta): {beta:.4f}")
    print(f"Damping Ratio (zeta): {zeta_ld:.4f}")
    print(f"R^2: {r_squared:.4f}")
    print(f"Plot saved to: {plot_path}")
    print(f"omega_d: {omega_d:.4f}")

    # Show the plot
    plt.show()
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.optimize import curve_fit
import os
from datetime import datetime
from tkinter import Tk
from tkinter.filedialog import askopenfilename

def find_damping_ratio(file_path=None):
    """
    Analyze accelerometer data from a selected numpy file or from the provided file path,
    fit it to an exponential decay curve, and save a plot of the results with relevant annotations.

    Args:
        file_path (str): The path to the numpy file. If not provided, a UI will prompt the user to select a file.

    Returns:
        None
    """
    if file_path is None:
        os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

        # Open a file selector window
        root = Tk()
        root.withdraw()  # Hide the root window
        file_path = askopenfilename(title="Select the numpy array file", filetypes=[("Numpy files", "*.npy")])

        if not file_path: 
            print("No file selected")
            return

    # Load the data from the selected file
    data = np.load(file_path)

    # Assuming data format: [timestamps, accelerometer_data]
    timestamps = data[0]
    accelerometer_data = data[1]

    max_acc = max(accelerometer_data)

    # Find the peaks in the accelerometer data with specified parameters
    if 3.98 < max_acc < 4.01 or 1.97 < max_acc < 2.02:
        peaks, _ = find_peaks(accelerometer_data, distance=500, height=(0.01, max_acc - 0.01), prominence=0.2)
    else:
        peaks, _ = find_peaks(accelerometer_data, distance=500, height=0.01, prominence=0.2)

    # Find the index of the maximum peak
    max_peak_index = np.argmax(accelerometer_data[peaks])

    # Remove peaks that are smaller than the maximum peak (i.e., have a smaller x-location)
    peaks = [peak for peak in peaks if peak > peaks[max_peak_index]]

    # Remove the first and last peaks
    if len(peaks) > 2:
        peaks = peaks[2:-4]

    # Extract peak times and values
    peak_times = timestamps[peaks]
    peak_values = accelerometer_data[peaks]

    # Calculate omega d in Hz using counting method by number of peaks per second
    omega_d = len(peak_times) / (peak_times[-1] - peak_times[0])

    # Logarithmic Decrement Method
    def exponential_decay(t, A0, beta):
        return A0 * np.exp(-beta * t)

    # Initial guesses for the parameters
    initial_guess = [peak_values[0], 1.0]

    # Fit the peak values to the exponential decay function
    popt, _ = curve_fit(exponential_decay, peak_times, peak_values, p0=initial_guess)

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
        f'omega_d: {omega_d:.4f}',
        f'R^2: {r_squared:.4f}'    
    ))
    plt.gcf().text(1-0.4, 0.6, textstr, fontsize=12, bbox=dict(facecolor='white', alpha=0.8))

    # Save the plot to the same directory as the opened file with higher resolution
    plot_path = os.path.splitext(file_path)[0] + "_log_decay_plot"
    run_time = datetime.now().strftime(f'%m-%d_%H-%M-%S_')

    plt.savefig(plot_path + run_time + ".png", dpi=600)  # Set dpi to 600 for higher resolution
    print(f"Initial Amplitude (A0): {A0:.4f}")
    print(f"Decay Rate (beta): {beta:.4f}")
    print(f"Damping Ratio (zeta): {zeta_ld:.4f}")
    print(f"R^2: {r_squared:.4f}")
    print(f"Plot saved to: {plot_path}")
    print(f"omega_d: {omega_d:.4f}")

    # Show the plot
    plt.show() 
find_damping_ratio()
