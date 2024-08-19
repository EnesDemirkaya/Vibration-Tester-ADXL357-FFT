#Scan_I2C_Devices.py

import smbus
import time

# Function to scan I2C bus for devices
def scan_i2c_bus(bus_number=1):
    i2c = smbus.SMBus(bus_number)
    devices = []
    
    for address in range(3, 128):
        try:
            i2c.write_quick(address)
            devices.append(hex(address))
        except:
            pass
    
    return devices

# Main function
while 1:
    print("Scanning I2C bus for devices...")
    devices = scan_i2c_bus()
    
    if devices:
        print(f"Found devices at addresses: {', '.join(devices)}")
    else:
        print("No I2C devices found.")
