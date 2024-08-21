import os
import sys
from save_plain_npy_fixed_samplerate import collect_accelerometer_data
from Play_Sweep_and_Record import play_and_record
from Plot_STFT_and_FFT import plot_fft_stft_from_file
from Damping_Ratio_Exponential_Decay import find_damping_ratio
from tkinter import Tk
from tkinter.filedialog import askopenfilename

# Global variable to store the last generated file path
last_saved_file_path = None

def menu():
    print("\n===== Accelerometer Data Processing Application =====")
    print("1. Collect Accelerometer Data")
    print("2. Play Sweep and Record Accelerometer Data")
    print("3. Plot FFT and STFT from Last File")
    print("4. Analyze Last Data File for Damping Ratio")
    print("5. Exit")
    print("=====================================================")

def get_file_path():
    global last_saved_file_path
    if last_saved_file_path and os.path.exists(last_saved_file_path):
        use_last = input("Do you want to use the last saved file? (y/n): ").strip().lower()
        if use_last == 'y':
            return last_saved_file_path
    # If user chooses not to use the last file or if no valid path exists, open file dialog
    print("Please select a file manually.")
    root = Tk()
    root.withdraw()  # Hide the main Tkinter window
    file_path = askopenfilename(title="Select the numpy file", filetypes=[("Numpy files", "*.npy")])
    if file_path and os.path.exists(file_path):
        last_saved_file_path = file_path  # Update the global path
        return file_path
    else:
        print("No valid file selected.")
        return None

def main():
    global last_saved_file_path
    os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor
    
    while True:
        menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            print("\nStarting data collection...")
            last_saved_file_path = collect_accelerometer_data()
            # collect_accelerometer_data should return the path where the data is saved

        elif choice == "2":
            print("\nStarting sweep and data recording...")
            last_saved_file_path = play_and_record()
            # play_and_record should return the path where the data is saved

        elif choice == "3":
            print("\nPlotting FFT and STFT from last saved file...")
            file_path = get_file_path()
            if file_path:
                plot_fft_stft_from_file(file_path=file_path)

        elif choice == "4":
            print("\nAnalyzing last saved file for damping ratio...")
            file_path = get_file_path()
            if file_path:
                find_damping_ratio(file_path=file_path,)

        elif choice == "5":
            print("Exiting the application.")
            sys.exit()

        else:
            print("Invalid choice. Please select a valid option.")

if __name__ == "__main__":
    main()
