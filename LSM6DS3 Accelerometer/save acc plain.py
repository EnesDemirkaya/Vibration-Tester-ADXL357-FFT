import os
import time
import numpy as np
from datetime import datetime
import smbus2 as smbus
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets

# I2C address
I2C_ADDRESS = 0x1D  # 0x1D for the ADXL357

# ADXL357 Register Addresses
REG_XDATA3 = 0x08
REG_YDATA3 = 0x0B
REG_ZDATA3 = 0x0E

# Initialize the I2C bus
bus = smbus.SMBus(1)

def read_accel_data():
    # Read 3 bytes for each axis
    x = bus.read_i2c_block_data(I2C_ADDRESS, REG_XDATA3, 3)
    y = bus.read_i2c_block_data(I2C_ADDRESS, REG_YDATA3, 3)
    z = bus.read_i2c_block_data(I2C_ADDRESS, REG_ZDATA3, 3)
    
    # Combine bytes and apply two's complement
    x_data = (x[0] << 12) | (x[1] << 4) | (x[2] >> 4)
    y_data = (y[0] << 12) | (y[1] << 4) | (y[2] >> 4)
    z_data = (z[0] << 12) | (z[1] << 4) | (z[2] >> 4)
    
    if x_data & (1 << 19): x_data -= (1 << 20)
    if y_data & (1 << 19): y_data -= (1 << 20)
    if z_data & (1 << 19): z_data -= (1 << 20)
    
    return x_data, y_data, z_data

def save_accelerometer_numpy(x_data, y_data, z_data, timestamps, run_time):
    np.save(os.path.join(run_time, 'accelerometer_data.npy'), np.array([timestamps, x_data, y_data, z_data]))

def collect_accelerometer_data():
    # Global variables for accelerometer data
    x_axis_data = []
    y_axis_data = []
    z_axis_data = []
    timestamps_data = []
    start_time = None
    last_time = None

    def init_ADXL357():
        # Setup can be customized here if needed
        pass  # No specific initialization required for reading from the ADXL357 over I2C

    def read_acc_data():
        nonlocal last_time
        try:
            # Read data
            x, y, z = read_accel_data()

            # Calculate the current time and elapsed time
            current_time = time.time()
            if last_time is not None:
                interval = current_time - last_time
                sampling_rate = 1 / interval
            else:
                interval = 0
                sampling_rate = 0
            last_time = current_time
            elapsed_time = current_time - start_time

            x_axis_data.append(x)
            y_axis_data.append(y)
            z_axis_data.append(z)
            timestamps_data.append(elapsed_time)

            print(f"X: {x}, Y: {y}, Z: {z}, Time: {elapsed_time:.6f}s, "
                  f"Sampling Rate: {sampling_rate:.2f} Hz")
        except Exception as e:
            print(f"Error: {e}")

    try:
        with open('last_run.txt', 'r') as file:
            last_duration = float(file.readline().strip())
            last_custom_name = file.readline().strip()
    except:
        last_duration = 10.0  # Default duration
        last_custom_name = "default_name"

    duration = float(input(f"Enter the duration for data collection (in seconds) [{last_duration}]: ") or last_duration)
    custom_name = input(f"Enter a custom name to append to the folder [{last_custom_name}]: ") or last_custom_name

    start_time = time.time()  # Initialize start_time
    last_time = start_time  # Initialize last_time

    init_ADXL357()

    # Create directory for the current run
    run_time = datetime.now().strftime(f'%m-%d_%H-%M-%S_{custom_name}')
    os.makedirs(run_time, exist_ok=True)

    # PyQtGraph setup for real-time plotting
    app = QtWidgets.QApplication([])
    win = pg.GraphicsLayoutWidget(show=True)
    win.setWindowTitle('ADXL357 Real-time Accelerometer Data')

    p1 = win.addPlot(title="X-Axis")
    p2 = win.addPlot(title="Y-Axis")
    p3 = win.addPlot(title="Z-Axis")

    curve_x = p1.plot(pen='r')
    curve_y = p2.plot(pen='g')
    curve_z = p3.plot(pen='b')

    timer = QtCore.QTimer()
    
    def update_plot():
        nonlocal last_time
        read_acc_data()

        # Keep only the last 5 seconds of data
        current_time = time.time() - start_time
        while timestamps_data and timestamps_data[0] < current_time - 5:
            x_axis_data.pop(0)
            y_axis_data.pop(0)
            z_axis_data.pop(0)
            timestamps_data.pop(0)

        curve_x.setData(timestamps_data, x_axis_data)
        curve_y.setData(timestamps_data, y_axis_data)
        curve_z.setData(timestamps_data, z_axis_data)

        app.processEvents()

    timer.timeout.connect(update_plot)
    timer.start(50)

    while (time.time() - start_time) < duration:
        QtWidgets.QApplication.instance().exec_()

    save_accelerometer_numpy(x_axis_data, y_axis_data, z_axis_data, timestamps_data, run_time)

    print(f"Data saved to directory: {run_time}")

    with open('last_run.txt', 'w') as file:
        file.write(f"{duration}\n")
        file.write(f"{custom_name}\n")

if __name__ == "__main__":
    collect_accelerometer_data()
