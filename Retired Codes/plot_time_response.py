import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

def plot_combined_graphs(acc_data_path=None, sweep_data_path=None):
    # If acc_data_path is not provided, open a file dialog to select the file
    if acc_data_path is None:
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        acc_data_path = filedialog.askopenfilename(filetypes=[("Numpy files", "*.npy")], title="Select Accelerometer Data File")
        if not acc_data_path:
            print("No accelerometer data file selected. Exiting...")
            return
    
    # Load accelerometer data
    acc_data = np.load(acc_data_path)
    timestamps_acc, waveform_acc = acc_data[0], acc_data[1]

    plt.figure(figsize=(12, 6))

    plt.subplot(2, 1, 1)
    plt.plot(timestamps_acc, waveform_acc, label='Accelerometer')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.title('Accelerometer Amplitude vs Time')

    if sweep_data_path:
        sweep_data = np.load(sweep_data_path)
        timestamps_sweep, waveform_sweep = sweep_data[0], sweep_data[1]

        plt.subplot(2, 1, 2)
        plt.plot(timestamps_sweep, waveform_sweep, label='Sweep')
        plt.xlabel('Time (s)')
        plt.ylabel('Amplitude')
        plt.title('Sweep Amplitude vs Time')

    plt.tight_layout()
    plt.savefig(os.path.join(os.path.dirname(acc_data_path), 'combined_plot.png'))
    plt.show()

if __name__ == "__main__":
    # Optional: You can pass paths directly or leave them as None to prompt the file dialog
    acc_data_path = None
    sweep_data_path = None  # Optional, set to None if not available

    plot_combined_graphs(acc_data_path, sweep_data_path)
