


## Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Hardware Setup](#hardware-setup)
   - [Wiring Table for ADXL357](#wiring-table-for-adxl357)
   - [Wiring Table for LSM6DS3 (Optional)](#wiring-table-for-lsm6ds3-optional)
4. [Setting Up I2C Speed](#setting-up-i2c-speed)
   - [Checking I2C Speed](#checking-i2c-speed)
   - [Changing I2C Speed to 400kHz](#changing-i2c-speed-to-400khz)
5. [Repository Structure and Code Explanation](#repository-structure-and-code-explanation)
   - [Folder Structure](#folder-structure)
   - [Code Descriptions](#code-descriptions)
     - [1. Check I2C Speed.py](#1-check-i2c-speedpy)
     - [2. Damping ratio Exponential Decay.py](#2-damping-ratio-exponential-decaypy)
     - [3. Plot STFT and FFT.py](#3-plot-stft-and-fftpy)
     - [4. save_plain_npy_fixed_samplerate.py](#4-save_plain_npy_fixed_sampleratepy)
6. [Usage Instructions](#usage-instructions)
   - [Recording Data](#recording-data)
   - [Analyzing Data](#analyzing-data)
7. [To-Do List](#to-do-list)
8. [Resources](#resources)
9. [License](#license)
10. [Contact](#contact)

## Overview

This repository contains a set of tools and scripts designed for performing modal and damping analysis of a cantilever beam using a Raspberry Pi 5. The system is set up to work with the ADXL357 accelerometer in I2C mode, with an option to use the LSM6DS3 accelerometer, for which relevant files are provided in the `LSM6DS3` folder. The project focuses on accurately recording and analyzing vibration data to extract meaningful information about the dynamic behavior of the cantilever beam.

## Requirements

- **Hardware:**
  - Raspberry Pi 5
  - ADXL357 Accelerometer (primary)
  - LSM6DS3 Accelerometer (optional)
  - Connecting wires

- **Software:**
  - Python 3.x
  - NumPy (for numerical computations)
  - PyQtGraph (for plotting)
  - smbus or smbus2 (for I2C communication)

### Installing Dependencies

You can install the required Python packages using `pip`:

```bash
pip install numpy pyqtgraph smbus smbus2
```

## Hardware Setup

### Wiring Table for ADXL357

| Raspberry Pi Pin | ADXL357 Pin | Description             |
|------------------|-------------|-------------------------|
| 3.3V             | VDD         | Power Supply            |
| GND              | GND         | Ground                  |
| GPIO 2 (SDA1)    | SDA         | I2C Data Line           |
| GPIO 3 (SCL1)    | SCL         | I2C Clock Line          |

### Wiring Table for LSM6DS3 (Optional)

| Raspberry Pi Pin | LSM6DS3 Pin | Description             |
|------------------|-------------|-------------------------|
| 3.3V             | VDD         | Power Supply            |
| GND              | GND         | Ground                  |
| GPIO 2 (SDA1)    | SDA         | I2C Data Line           |
| GPIO 3 (SCL1)    | SCL         | I2C Clock Line          |

## Setting Up I2C Speed

To achieve a high sampling rate with the ADXL357, the I2C speed on the Raspberry Pi should be set to 400kHz. Below are instructions to verify and change the I2C speed.

### Checking I2C Speed

Use the `Check I2C Speed.py` script to verify the current I2C speed:

```bash
python "Check I2C Speed.py"
```

### Changing I2C Speed to 400kHz

1. Open the `/boot/config.txt` file:

   ```bash
   sudo nano /boot/config.txt
   ```

2. Add or modify the following line to set the I2C speed:

   ```bash
   dtparam=i2c_arm_baudrate=400000
   ```

3. Save the file and exit the editor (Ctrl+X, then Y, and Enter).

4. Reboot your Raspberry Pi to apply the changes:

   ```bash
   sudo reboot
   ```

## Repository Structure and Code Explanation

### Folder Structure

- **`ADXL357/`**: Contains scripts and tools specifically for the ADXL357 accelerometer.
- **`LSM6DS3/`**: Contains scripts for the LSM6DS3 accelerometer.
- **`Recordings/`**: A folder with recorded data and numpy array files for later comparison.
- **`Check I2C Speed.py`**: Script to check the I2C communication speed on the Raspberry Pi.
- **`Damping ratio Exponential Decay.py`**: Script to calculate the damping ratio using the exponential decay method.
- **`Plot STFT and FFT.py`**: Script to generate and visualize the Short-Time Fourier Transform (STFT) and Fast Fourier Transform (FFT) of the accelerometer data.
- **`save_plain_npy_fixed_samplerate.py`**: Script to save accelerometer data with a fixed sampling rate.

### Code Descriptions

#### 1. `Check I2C Speed.py`

This script checks the current I2C bus speed on the Raspberry Pi. It helps ensure that the I2C bus is set to the correct speed (400kHz) to allow high-frequency data sampling from the accelerometers.

#### 2. `Damping ratio Exponential Decay.py`

This script calculates the damping ratio of the cantilever beam using the exponential decay method. The damping ratio is a crucial parameter in understanding how quickly vibrations diminish over time, indicating the amount of energy lost during each oscillation cycle.

- **Input:** Accelerometer data recorded during the beam's oscillation.
- **Output:** Damping ratio value that indicates how quickly the system's vibrations are dying out.

#### 3. `Plot STFT and FFT.py`

This script plots both the Short-Time Fourier Transform (STFT) and the Fast Fourier Transform (FFT) of the accelerometer data. These frequency analysis tools are used to understand the frequency components of the vibrations over time and can provide insights into the dynamic behavior of the cantilever beam.

- **STFT:** Helps analyze how the frequency content of the signal evolves over time.
- **FFT:** Provides a snapshot of the frequency content of the entire signal.

#### 4. `save_plain_npy_fixed_samplerate.py`

This script saves the accelerometer data to a numpy file while maintaining a fixed sample rate. Consistent sampling is vital for accurate analysis, and this script ensures that the data is uniformly sampled.

- **Usage:** Run this script within the desired directory to record and save data for later analysis.
- **Output:** A numpy file containing the recorded accelerometer data.

### Usage Instructions

#### Recording Data

1. Navigate to the desired folder where you want to save the data:

   ```bash
   cd path/to/folder
   ```

2. Run the recording script to collect data at a fixed sample rate:

   ```bash
   python save_plain_npy_fixed_samplerate.py
   ```

#### Analyzing Data

- **Damping Ratio Calculation:** Use the `Damping ratio Exponential Decay.py` script to calculate the damping ratio of the cantilever beam.

  ```bash
  python "Damping ratio Exponential Decay.py"
  ```

- **Frequency Analysis:** Use the `Plot STFT and FFT.py` script to visualize the frequency content of the accelerometer data.

  ```bash
  python "Plot STFT and FFT.py"
  ```

## To-Do List

- Implement FIFO (First-In, First-Out) buffering for a more stable sample rate. This will further improve the accuracy and reliability of the measured peak frequency.

## Resources

https://www.analog.com/en/products/adxl357.html
https://en.wikipedia.org/wiki/Short-time_Fourier_transform
https://en.wikipedia.org/wiki/Fast_Fourier_transform
## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For questions, feedback, or support, please reach out to [Enes Demirkaya](mailto:demirkaya.e@northeastern.edu).

