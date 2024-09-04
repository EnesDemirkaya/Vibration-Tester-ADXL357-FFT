
# Modal and Damping Analysis of a Cantilever Beam

## Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Nomenclature](#nomenclature)
4. [Setup](#setup)
   - [Wiring](#wiring)
   - [Remote Connection (VNC and SSH) (Optional)](#remote-connection-vnc-and-ssh-optional)
   - [Sound Output](#sound-output)
5. [Repository Structure and Code Explanation](#repository-structure-and-code-explanation)
   - [Folder Structure](#folder-structure)
   - [Code Descriptions](#code-descriptions)
6. [Usage Procedure](#usage-procedure)
   - [Recording Data](#recording-data)
   - [Analyzing Data](#analyzing-data)
   - [Beam with Tip Mass Computational Natural Frequencies](#beam-with-tip-mass-computational-natural-frequencies)
7. [MATLAB Codes](#matlab-codes)
   - [Natural Frequency vs Length with Comparison with Experimental](#explanation-for-leonard3_only_length_measured_peaksmlx)
   - [Mode Shapes with Tip Mass](#explanation-for-leonard3_only_length_measured_peaksmlx)
8. [To-Do List](#to-do-list)
9. [Resources](#resources)
10. [License](#license)
11. [Contact](#contact)
12. [Additional Components](#additional-components)

## Overview

This repository contains a set of tools and scripts designed for performing modal and damping analysis of a cantilever beam using a Raspberry Pi 5. The system is set up to work with the ADXL357 accelerometer in I2C mode, with an option to use the LSM6DS3 accelerometer, for which relevant files are provided in the `LSM6DS3` folder. The project focuses on accurately recording and analyzing vibration data to extract meaningful information about the dynamic behavior of the cantilever beam.

## Requirements

- **Hardware:**
  - Raspberry Pi (5)
  - ADXL357 Accelerometer (primary)
  - LSM6DS3 Accelerometer (optional)
  - Connecting wires
  - Beam (e.g., Aluminum or HDPE)
  - Sound Amplifier (optional)
  - Vise for securing the beam and granular box

- **Software:**
  - Python 3.x
  - NumPy (for numerical computations)
  - PyQtGraph (for plotting)
  - smbus or smbus2 (for I2C communication)
  - VSCode with Remote-SSH extension (optional)
  - VNC Viewer for remote desktop access (optional)

### Installing Dependencies

You can install the required Python packages using `pip`:

```bash
pip install numpy pyqtgraph smbus smbus2
```

## Nomenclature

- **Acc:** Accelerometer (ADXL357)
- **Old acc:** Legacy accelerometer (LSM6DS3)
- **FFT:** Fast Fourier Transform
- **STFT:** Short Time Fourier Transform
- **SSH:** Secure Shell protocol for securely sending commands to a computer over an unsecured network.
- **VNC:** Virtual Network Computing, a graphical desktop-sharing system using the Remote Frame Buffer protocol to control another computer remotely.

## Setup

### Wiring

1. **Install the Beam and Granular Box:**
   - Secure the beam and granular box using a vise.

2. **Wire the Accelerometer:**
   - Wire the harness according to general I2C connections.
   - **Important:** Use both grounds and both VCCs in the ADXL357. Ensure you use **3.3V, NOT 5V**.
   - Attach the accelerometer to the beam and secure the wiring to prevent oscillation like a pendulum.

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

### Remote Connection (VNC and SSH) (Optional)

1. **Connect Raspberry Pi to the Internet:**
   - Use an Ethernet connection to ensure a static IP address (e.g., `129.10.126.255`).
   
2. **SSH into Raspberry Pi:**
   - **Install the Remote-SSH Extension in VSCode:**
     - Open VSCode, press `Ctrl + Shift + X`, search for "Remote - SSH," and install it.
   - **Add New SSH Host:**
     - Open the Command Palette (`Ctrl + Shift + P`).
     - Type `Remote-SSH: Connect to Host...` and select it.
     - Enter the SSH connection string in the format: `ssh cslab@<IP address>` (e.g., `ssh cslab@129.10.126.255`).
     - Press Enter and follow the prompts to add this to your SSH configuration file with a friendly name like `cslab`.
   - **Enter the Password:**
     - When prompted, enter the password for the `cslab` user.
   - **Select Python Interpreter:**
     - Once connected, select the Python interpreter located at `/usr/bin/python3` on the Raspberry Pi. If you don’t see a prompt, manually select the Python interpreter by opening the Command Palette (`Ctrl + Shift + P`) and typing `Python: Select Interpreter`.

3. **VNC Connection:**
   - For applications requiring a display (like GUI or plots), ensure remote desktop access via VNC is configured on the Raspberry Pi or use a monitor.
   - **Connect using VNC Viewer:**
     - Username: `cslab`
   - Download VNC Viewer from [RealVNC](https://www.realvnc.com/en/connect/download/viewer/).

4. **Display Configuration:**
   - When running code that executes a window (e.g., a UI or plot), sometimes it encounters an issue finding a display because the user ran the code through SSH. To fix this, set the display environment variable manually in the code using:
   ```python
   os.environ['DISPLAY'] = ':0'  # to run the code from SSH but show on the monitor
   ```
   - This is normally set up automatically when logging into a desktop environment. For more details, see [What is DISPLAY=:0?](https://unix.stackexchange.com/questions/193827/what-is-display-0).

### Sound Output

- The Raspberry Pi 5 lacks a sound output jack. To output sound:
  - Use a USB/HDMI to aux adapter.
  - Alternatively, use a monitor with an aux out, ensuring the monitor is turned on.

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
- **FFT:** Provides a snapshot of the frequency content of the entire

 signal. Used to find frequency peaks aka natural freq of the recording

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

## Usage Procedure

### Reconnect to Remote Host via VSCode Remote

- Ensure that your Raspberry Pi is connected to the network and accessible via SSH using the steps described in the [Remote Connection (VNC and SSH)](#remote-connection-vnc-and-ssh-optional) section.
- Enter the `Vibration-Tester-ADXL357-FFT` folder on the Raspberry Pi's Desktop.

### Recording Data

1. **Create a Folder for Data:**
   - Use `mkdir` and `cd` to create and enter a folder where you will record the data.

2. **Run the Recording Script:**
   - **If sound generation is required:** Run the `Play_Sweep_and_Record.py` script to play a sweep sound while recording.
   - **If no sound generation is required:** Run the `save_plain_npy_fixed_samplerate.py` script.

### Analyzing Data

1. **Damping Ratio Calculation:**
   - Use the `Damping ratio Exponential Decay.py` script to analyze the data and generate plots showing the exponential decay fit and identified peaks.

2. **Frequency Analysis:**
   - Use the `Plot STFT and FFT.py` script to visualize the frequency content of the accelerometer data.

### Beam with Tip Mass Computational Natural Frequencies

1. **Run the MATLAB Code:**
   - Run one of the MATLAB codes according to the beam parameters you want to iterate over. Edit the values defined at the beginning of the code.
   - Change the eigenvalue iteration final value to find more or fewer modes.

2. **Edit the Excel File:**
   - Update the `points_data.xlsx` file in the same folder to change the plot of the measured natural frequencies. This is essential for comparing the computational results with experimental data.

## MATLAB Codes

### Explanation for `leonard3_only_length_measured_peaks.mlx`
![alt text](https://github.com/EnesDemirkaya/Vibration-Tester-ADXL357-FFT/blob/4c31f2518591db9c4d7b30df0d6ffec5a7e070e7/Natural_Freq_Calculation_MATLAB/Example%20Output%20Figures/2D_Plot_TipMass_5g_Material_Aluminum_Width_50mm.png?raw=true)

#### Overview
This MATLAB script calculates the natural frequencies of a cantilever beam with a tip mass using both analytical methods and compares these to experimentally measured frequencies. The script iterates over different beam lengths and computes the natural frequencies for each length. The calculated frequencies are then compared with measured frequencies recorded in a spreadsheet, and the results are plotted.

#### Steps in the Script

1. **Initialization of Beam Parameters:**
   - **`Bb = 50 mm`:** Width of the beam.
   - **`d = 2700 kg/m³`:** Density of the beam material (aluminum in this case).
   - **`E = 70e9 Pa`:** Modulus of elasticity of the beam material.
   - **`Mt = 5 g`:** Tip mass attached to the free end of the beam.
   - **`L_values`:** A range of beam lengths over which the natural frequencies will be calculated.
   - **`Db = 2 mm`:** Depth of the beam.

   *Note: These parameters should be adjusted if you are using a different material or if the experiment involves different dimensions or a different tip mass.*

2. **Symbolic Equations:**
   - The characteristic equation of the beam, including the tip mass effect, is defined using symbolic variables in MATLAB. This equation is essential for determining the natural frequencies by solving for the values of `βL`, where `L` is the beam length.

   - The equation used corresponds to the one shown in the image, where `m` is the mass per unit length of the beam, and `M` is the mass attached at the free end.

3. **Iteration Over Lengths:**
   - For each length in `L_values`, the script:
     - Calculates the mass of the beam and the moment of inertia.
     - Constructs the characteristic equation specific to that length.
     - Solves for the first four solutions of `βL` using `vpasolve`.
     - Calculates the natural frequencies (`fn`) from these solutions and stores them.

4. **Comparison with Experimental Data:**
   - The script reads experimentally measured natural frequencies from a spreadsheet (`points_data.xlsx`). This data must be updated manually after recording the peaks via FFT analysis from actual experimental data. Each row in the spreadsheet should contain the length of the beam, the measured frequency, and the corresponding mode number.

   - The script then plots the calculated natural frequencies against the lengths and overlays the experimentally measured frequencies for comparison.

5. **Visualization:**
   - The script generates a 2D plot with the length of the beam on the x-axis and the natural frequencies on the y-axis (logarithmic scale).
   - It also adds annotations to the plot, indicating the beam material, dimensions, and tip mass.

6. **Output:**
   - The generated plot is saved in an output folder as both a `.png` and a `.fig` file. The filename includes details about the tip mass, beam material, and beam width for easy identification.

#### Important Notes:

- **Updating the Spreadsheet:** After performing an experiment and recording the natural frequencies via FFT analysis, update the spreadsheet with the new frequencies and mode numbers corresponding to the different beam lengths. This step is crucial for accurate comparison and validation of the calculated frequencies.

- **Modifying Parameters:** If the material, dimensions, or tip mass change for a new experiment, you must update the corresponding variables (`Bb`, `d`, `E`, `Mt`, `Db`) at the beginning of the script. This ensures that the calculations reflect the new setup and provide accurate results.

### Explanation for `ModeShapeTipMassRitz.mlx`


![alt text](https://github.com/EnesDemirkaya/Vibration-Tester-ADXL357-FFT/blob/4c31f2518591db9c4d7b30df0d6ffec5a7e070e7/Natural_Freq_Calculation_MATLAB/Example%20Output%20Figures/ModeShapes.png?raw=true)

#### Overview
This MATLAB script calculates the mode shapes of a cantilever beam with a tip mass using both analytical methods.



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

