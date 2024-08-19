Modal and Damping Analysis of a Cantilever Beam

Contents

Overview
Requirements
Hardware Setup
Wiring Table for ADXL357
Wiring Table for LSM6DS3 (Optional)
Setting Up I2C Speed
Checking I2C Speed
Changing I2C Speed to 400kHz
Repository Structure and Code Explanation
Folder Structure
Code Descriptions
1. Check I2C Speed.py
2. Damping ratio Exponential Decay.py
3. Plot STFT and FFT.py
4. save_plain_npy_fixed_samplerate.py
Usage Instructions
Recording Data
Analyzing Data
To-Do List
Resources
License
Contact
Overview

This repository contains a set of tools and scripts designed for performing modal and damping analysis of a cantilever beam using a Raspberry Pi 5. The system is set up to work with the ADXL357 accelerometer in I2C mode, with an option to use the LSM6DS3 accelerometer, for which relevant files are provided in the LSM6DS3 folder. The project focuses on accurately recording and analyzing vibration data to extract meaningful information about the dynamic behavior of the cantilever beam.

Requirements

Hardware:
Raspberry Pi 5
ADXL357 Accelerometer (primary)
LSM6DS3 Accelerometer (optional)
Connecting wires
Software:
Python 3.x
NumPy (for numerical computations)
PyQtGraph (for plotting)
smbus or smbus2 (for I2C communication)
Installing Dependencies
You can install the required Python packages using pip:

bash
Copy code
pip install numpy pyqtgraph smbus smbus2
Hardware Setup

Wiring Table for ADXL357
Raspberry Pi Pin	ADXL357 Pin	Description
3.3V	VDD	Power Supply
GND	GND	Ground
GPIO 2 (SDA1)	SDA	I2C Data Line
GPIO 3 (SCL1)	SCL	I2C Clock Line
Wiring Table for LSM6DS3 (Optional)
Raspberry Pi Pin	LSM6DS3 Pin	Description
3.3V	VDD	Power Supply
GND	GND	Ground
GPIO 2 (SDA1)	SDA	I2C Data Line
GPIO 3 (SCL1)	SCL	I2C Clock Line
Setting Up I2C Speed

To achieve a high sampling rate with the ADXL357, the I2C speed on the Raspberry Pi should be set to 400kHz. Below are instructions to verify and change the I2C speed.

Checking I2C Speed
Use the Check I2C Speed.py script to verify the current I2C speed:

bash
Copy code
python "Check I2C Speed.py"
Changing I2C Speed to 400kHz
Open the /boot/firmware/config.txt file:
bash
Copy code
sudo nano /boot/firmware/config.txt
Add or modify the following line to set the I2C speed:
bash
Copy code
dtparam=i2c_arm_baudrate=400000
Save the file and exit the editor (Ctrl+X, then Y, and Enter).
Reboot your Raspberry Pi to apply the changes:
bash
Copy code
sudo reboot
Repository Structure and Code Explanation

Folder Structure
ADXL357/: Contains scripts and tools specifically for the ADXL357 accelerometer.
LSM6DS3/: Contains scripts for the LSM6DS3 accelerometer.
Recordings/: A folder with recorded data and numpy array files for later comparison.
Check I2C Speed.py: Script to check the I2C communication speed on the Raspberry Pi.
Damping ratio Exponential Decay.py: Script to calculate the damping ratio using the exponential decay method.
Plot STFT and FFT.py: Script to generate and visualize the Short-Time Fourier Transform (STFT) and Fast Fourier Transform (FFT) of the accelerometer data.
save_plain_npy_fixed_samplerate.py: Script to save accelerometer data with a fixed sampling rate.
Code Descriptions
1. Check I2C Speed.py

This script checks the current I2C bus speed on the Raspberry Pi. It helps ensure that the I2C bus is set to the correct speed (400kHz) to allow high-frequency data sampling from the accelerometers.

2. Damping ratio Exponential Decay.py

This script calculates the damping ratio of the cantilever beam using the exponential decay method. The damping ratio is a crucial parameter in understanding how quickly vibrations diminish over time, indicating the amount of energy lost during each oscillation cycle.

Input: Accelerometer data recorded during the beam's oscillation.
Output: Damping ratio value that indicates how quickly the system's vibrations are dying out.
3. Plot STFT and FFT.py

This script, now using the plot_fft_stft_from_file function, generates and visualizes both the Short-Time Fourier Transform (STFT) and the Fast Fourier Transform (FFT) of the accelerometer data. These frequency analysis tools are used to understand the frequency components of the vibrations over time and can provide insights into the dynamic behavior of the cantilever beam.

STFT: Helps analyze how the frequency content of the signal evolves over time.
FFT: Provides a snapshot of the frequency content of the entire signal.
Usage: You can use this script directly to visualize the frequency content of your data by either selecting the data file through a file dialog or by specifying the file path directly in the function call.
4. save_plain_npy_fixed_samplerate.py

This script saves the accelerometer data to a numpy file while maintaining a fixed sample rate. Consistent sampling is vital for accurate analysis, and this script ensures that the data is uniformly sampled.

Usage: Run this script within the desired directory to record and save data for later analysis.
Output: A numpy file containing the recorded accelerometer data.
Usage Instructions
Recording Data

Navigate to the desired folder where you want to save the data:
bash
Copy code
cd path/to/folder
Run the recording script to collect data at a fixed sample rate:
bash
Copy code
python save_plain_npy_fixed_samplerate.py
Analyzing Data

Damping Ratio Calculation: Use the Damping ratio Exponential Decay.py script to calculate the damping ratio of the cantilever beam.
bash
Copy code
python "Damping ratio Exponential Decay.py"
Frequency Analysis Using STFT and FFT:
To visualize the STFT and FFT of your recorded data, run the Plot STFT and FFT.py script. The script allows you to either choose the data file through a file dialog or provide the file path directly.
bash
Copy code
python "Plot STFT and FFT.py"
Custom Example:
If you want to analyze a specific file and apply smoothing to the FFT plot, you can modify the script to include the following:
python
Copy code
from Plot_STFT_and_FFT import plot_fft_stft_from_file

# Example usage:
plot_fft_stft_from_file(file_path="path/to/your/data.npy", smoothing=50)
Steps to Run the Analysis:
If you prefer to select the file interactively, just run the script, and a file dialog will appear to let you choose your .npy file.
Alternatively, if you know the file path, you can modify the script to include the path directly and specify the smoothing level.
The script will generate and display both the STFT and FFT plots and save them in the same directory as the data file.
To-Do List

Implement FIFO (First-In, First-Out) buffering for a more stable sample rate. This will further improve the accuracy and reliability of the recorded data.
Resources

ADXL357 Accelerometer Information
Short-Time Fourier Transform (STFT) on Wikipedia
Fast Fourier Transform (FFT) on Wikipedia
License

This project is licensed under the MIT License. See the LICENSE file for more details.

Contact

For questions, feedback, or support, please reach out to Enes Demirkaya.
