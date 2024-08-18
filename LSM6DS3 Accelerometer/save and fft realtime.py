# main_app.py
import os
os.environ['DISPLAY'] = ':0'  # to run the code from ssh but show on the monitor

import sys
import os
import time
import numpy as np
from datetime import datetime
import smbus
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from collections import deque
from threading import Thread, Lock
from itertools import islice

# I2C bus initialization
bus = smbus.SMBus(1)

# Constants
sensitivity = 0.061 * 4
LSM6DS3_ADDR = 0x6A
CTRL1_XL = 0x10
CTRL2_G = 0x11
CTRL3_C = 0x12
CTRL6_C = 0x15
CTRL8_XL = 0x17
OUTZ_L_XL = 0x2C
OUTZ_H_XL = 0x2D

freq = 2000  # 1/T
guarda = 6000  # 500
frequencia = np.linspace(0.0, 1.0/(2.0*1/freq), freq//2)

acelx = deque([], maxlen=guarda)
data = []
hanning_window = np.hanning(guarda)  # Hanning window

# PyQtGraph setup
app = QtWidgets.QApplication([])
win = pg.GraphicsLayoutWidget(show=True, title="Accelerometer Data")
win.resize(1000, 600)
win.setWindowTitle('Espectro')
pg.setConfigOption('foreground', 'w')

p1 = win.addPlot(title="Accelerometer")
linha1 = pg.mkPen((0, 255, 0), width=2)
p1.addLegend(offset=(10, 5))
curve1 = p1.plot(acelx, pen=linha1, name="X")
p1.setRange(yRange=[-5, 5], xRange=[0, 500])
p1.setLabel('bottom', text="Time")
p1.showGrid(x=True, y=False)

win.nextRow()
p2 = win.addPlot()
linha4 = pg.mkPen((255, 0, 0), width=2)
p2.addLegend(offset=(10, 5))
curve2 = p2.plot(frequencia, pen=linha4, name="Amplitude")
p2.setRange(xRange=[0, int(freq/2)])
p2.setLabel('bottom', text="Frequency (Hz)")
p2.showGrid(x=False, y=True)
ax = p2.getAxis('bottom')
ax.setTicks([[(v, str(v)) for v in np.arange(0, int(freq/2)+1, 100)]])

# Initialize LSM6DS3
def init_LSM6DS3():
    bus.write_byte_data(LSM6DS3_ADDR, CTRL1_XL, 0b10101100)
    bus.write_byte_data(LSM6DS3_ADDR, CTRL2_G, 0x00)
    bus.write_byte_data(LSM6DS3_ADDR, CTRL3_C, 0x44)
    bus.write_byte_data(LSM6DS3_ADDR, CTRL6_C, 0x10)
    bus.write_byte_data(LSM6DS3_ADDR, CTRL8_XL, 0x09)

# Read accelerometer data
def read_acc_data():
    global data
    while True:
        try:
            z_l = bus.read_byte_data(LSM6DS3_ADDR, OUTZ_L_XL)
            z_h = bus.read_byte_data(LSM6DS3_ADDR, OUTZ_H_XL)
            z = (z_h << 8 | z_l)
            if z >= 32768:
                z -= 65536
            z_g = z * sensitivity / 1000

            acelx.append(z_g)
            if len(acelx) == guarda:
                windowed_data = np.array(acelx) * hanning_window  # Apply the Hanning window
                data = np.fft.fft(windowed_data)
        except Exception as e:
            print(f"Error: {e}")

# Start data input thread
def data_input():
    read_acc_data()

t = Thread(target=data_input)
t.daemon = True
t.start()

# Update function for PyQtGraph
def update():
    curve1.setData(deque(islice(acelx, 1500, 2000), maxlen=500))
    if len(acelx) == guarda:
        curve2.setData(2/guarda * np.abs(data[:guarda//2]))

timer = pg.QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)

if __name__ == '__main__':
    init_LSM6DS3()
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtWidgets.QApplication.instance().exec_()
