
# ----------------------------------------------------------------------------
#File: examples.py
import time
import sys
from adxl355 import ADXL357

device = ADXL357()  
time.sleep(10)       
shadow_regs = device.read_shadowreg()
for i in range(10):
    print(i)    
    device.reset(shadow_regs)
time.sleep(10)
print(device.get_deviceid())
time.sleep(10)
status = device.get_status()
print(status)

while True:
    temp = device.get_temperature()
    print(temp)
    status = device.get_status()
    print(status)
    val = device.get_fifoentries()
    print(val)
    axes = device.get_axes() 
    print(axes)