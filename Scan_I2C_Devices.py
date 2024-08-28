#Scan_I2C_Devices.py

import smbus
import time

# Function to scan I2C bus for devices
def scan_i2c_bus(bus_number=1):
    """
    Scan the I2C bus for connected devices.

    This function scans the specified I2C bus for any devices by attempting to 
    communicate with each address in the valid range (0x03 to 0x7F). If a device 
    responds, its address is added to the list of found devices.

    Args:
        bus_number (int): The I2C bus number to scan. Default is 1, which is typical 
                          for many Raspberry Pi models.

    Returns:
        list of str: A list of hex-formatted addresses where devices were found.
    """
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
    """
    Continuously scan the I2C bus for devices and print the results.

    This loop repeatedly scans the I2C bus using `scan_i2c_bus()` and prints the 
    addresses of any detected devices. If no devices are found, a message indicating 
    this is printed. The loop runs indefinitely.
    """
    print("Scanning I2C bus for devices...")
    devices = scan_i2c_bus()
    
    if devices:
        print(f"Found devices at addresses: {', '.join(devices)}")
    else:
        print("No I2C devices found.")
