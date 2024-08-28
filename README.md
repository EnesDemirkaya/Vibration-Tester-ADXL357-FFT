# Modal and Damping Analysis of a Cantilever Beam

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
     - [4. save_plain_npy_fixed_samplerate.py](#4-save_plain_npy-fixed-sampleratepy)
6. [Usage Instructions](#usage-instructions)
   - [Recording Data](#recording-data)
   - [Analyzing Data](#analyzing-data)
7. [To-Do List](#to-do-list)
8. [Resources](#resources)
9. [License](#license)
10. [Contact](#contact)
11. [Additional Components](#additional-components)

## Overview

This repository contains a set of tools and scripts designed for performing modal and damping analysis of a cantilever beam using a Raspberry Pi 5. The system is set up to work with the ADXL357 accelerometer in I2C mode, with an option to use the LSM6DS3 accelerometer, for which relevant files are provided in the `LSM6DS3` folder. The project focuses on accurately recording and analyzing vibration data to extract meaningful information about the dynamic behavior of the cantilever beam.

## Requirements

- **Hardware:**
  - Raspberry Pi (5)
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
| 3.3V             | VDD VCC     | Power Supply            |
| GND              | GND GND     | Ground                  |
| GPIO 2 (SDA1)    | SDA         | I2C Data Line           |
| GPIO 3 (SCL1)    | SCL         | I2C Clock Line          |

**Warning:** Use both GND and VCC of the sensor, use 3.3V NOT 5V.

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

1. Open the `/boot/firmware/config.txt` file:

   ```bash
   sudo nano /boot/firmware/config.txt
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

- **`LSM6DS3 Accelerometer/`**: Contains scripts for the LSM6DS3 accelerometer.
- **`Example Recordings/`**: A folder with recorded data and numpy array files for later comparison.
- **`Check I2C Speed.py`**: Script to check the I2C communication speed on the Raspberry Pi.
- **`Damping ratio Exponential Decay.py`**: Script to calculate the damping ratio using the exponential decay method.
- **`Plot STFT and FFT.py`**: Script to generate and visualize the Short-Time Fourier Transform (STFT) and Fast Fourier Transform (FFT) of the accelerometer data.
- **`save_plain_npy_fixed_samplerate.py`**: Script to save accelerometer data with a fixed sampling rate.
- **`Play_Sweep_and_Record.py`**: Script to save accelerometer data while playing a sweep sound for the shaker.

### Code Descriptions

#### 1. `Check I2C Speed.py`

This script checks the current I2C bus speed on the Raspberry Pi. It helps ensure that the I2C bus is set to the correct speed (400kHz) to allow high-frequency data sampling from the accelerometers.

#### 2. `Damping ratio Exponential Decay.py`

This script calculates the damping ratio of the cantilever beam using the exponential decay method. The damping ratio is a crucial parameter in understanding how quickly vibrations diminish over time, indicating the amount of energy lost during each oscillation cycle.

- **Input:** Numpy array of accelerometer data recorded during the beam's oscillation.
- **Output:** Damping ratio value that indicates how quickly the system's vibrations are dying out, filepath of the saved time response plot with found peaks and decay envelope.

#### 3. `Plot STFT and FFT.py`

This script plots both the Short-Time Fourier Transform (STFT) and the Fast Fourier Transform (FFT) of the accelerometer data.

- **STFT:** Helps analyze how the frequency content of the signal evolves over time. Used to compare how the recording went.
- **FFT:** Provides a snapshot of the frequency content of the entire signal. Used to find frequency peaks aka natural freq of the recording

**Key Features:**

- **Smoothing:** A smoothing factor can be applied to the FFT plot to reduce noise and provide a clearer view of the frequency content. This is useful for identifying peaks that might be obscured by noise.
  
- **Windowing:** You can apply various window functions (e.g., Hann, Hamming) to the data before performing the FFT or STFT. Windowing helps reduce spectral leakage, which occurs when the signal is not perfectly periodic within the sampling window. This improves the accuracy of the frequency analysis, especially when dealing with transient signals. [Learn more about Window Functions](https://en.wikipedia.org/wiki/Window_function).

- **Zero Padding:** This technique involves adding zeros to the end of the signal before performing the FFT. Zero padding does not increase the actual frequency resolution, but it can improve the visual representation of the spectrum by creating a finer grid of frequency points. [Read about Zero Padding](https://en.wikipedia.org/wiki/Zero_padding).

- **Peak Annotation:** The script can automatically detect and annotate peaks in the FFT plot. This helps in identifying the natural frequencies of the beam and other significant frequency components.

- **Scale Options:** The script supports both linear and logarithmic scales for both the magnitude and frequency axes. Logarithmic scaling is particularly useful for analyzing signals with a wide dynamic range or identifying harmonics and other low-amplitude components. [Learn about FFT](https://en.wikipedia.org/wiki/Fast_Fourier_transform).

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

   - **To only save:** (optionally make volume zero and use the second option)

     ```bash
     python save_plain_npy_fixed_samplerate.py
     ```

   - **To play sweep sound while saving:** (Make sure volume level is decent)

     ```bash
     python Play_Sweep_and_Record.py
     ```

#### Analyzing Data

- **Damping Ratio Calculation:** Use the

 `Damping ratio Exponential Decay.py` script to calculate the damping ratio of the cantilever beam.

  ```bash
  python "Damping ratio Exponential Decay.py"
  ```

- **Frequency Analysis:** Use the `Plot STFT and FFT.py` script to visualize the frequency content of the accelerometer data.

  ```bash
  python "Plot STFT and FFT.py"
  ```

## To-Do List

- Implement FIFO (First-In, First-Out) buffering for a more stable sample rate. This will further improve the accuracy and reliability of the recorded data.

## Resources

- [ADXL357 Accelerometer Information](https://www.analog.com/en/products/adxl357.html)
- [Short-Time Fourier Transform (STFT) on Wikipedia](https://en.wikipedia.org/wiki/Short-time_Fourier_transform)
- [Fast Fourier Transform (FFT) on Wikipedia](https://en.wikipedia.org/wiki/Fast_Fourier_transform)
- https://www.youtube.com/watch?v=2dZPAv0q-9U

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For questions, feedback, or support, please reach out to [Enes Demirkaya](mailto:demirkaya.e@northeastern.edu).

## Additional Components

Below is a list of additional components used in this project:

### Mechanical Components

1. **Vise**: Versatile holder, 3.3" Movable Home Vice for Woodworking
   - [Link](https://a.co/d/04vnlsl4)
   - Price: $35

2. **HDPE Beam**: 1" Wide x 1/8" Thick x 4 Feet Long
   - [Link](https://a.co/d/04vnlsl4) (McMaster-Carr SKU: 8671K11)
   - Price: $20

3. **Aluminum Beam**: 0.08" Thick, 2" x 48"
   - [Link](https://a.co/d/04vnlsl4) (McMaster-Carr SKU: 89015K78)
   - Price: $20

4. **Granular Box**: To be 3D printed, has an attachment point for masses
   - Price: [N/A] (To be 3D printed)

### Electronics Components

1. **Power Amplifier**: Kinter K3118 Texas Instruments TI Digital Hi-Fi Audio Mini Class D Home Auto DIY Arcade Stereo Amplifier with 12V 3A Power Supply
   - [Link](https://a.co/d/03ZnHkR6)
   - Price: $26

2. **Vibration Generator**: EISCO Vibration Generator, Total Frequency Range: 1 to 5 kHz
   - [Link](https://a.co/d/0ieYArgP)
   - Price: $160

3. **Cable between Generator and Amplifier**: 4MM Banana Plug Test Cables
   - [Link](https://a.co/d/0iabKKZL)
   - Price: $8

4. **Auxiliary Cable**: 3.5mm Auxiliary Audio Cable
   - [Link](https://a.co/d/03imwwhy)
   - Price: $3

5. **Raspberry Pi**: Raspberry Pi 5 Starter Kit
   - [Link](https://a.co/d/09lTtMxA)
   - Price: $160

6. **Touchscreen Monitor**: 5 Inch Touchscreen Monitor for Raspberry Pi
   - [Link](https://a.co/d/0hKdGiNQ)
   - Price: $40

7. **MEMS Accelerometer**: ADXL357 Evaluation Board
   - [Link](https://www.digikey.com/short/pv871vbd) (Part Number: EVAL-ADXL357Z)
   - Price: $45

---

This additional component list will help ensure that all necessary parts are accounted for and easily accessible for replicating or building upon this project.
