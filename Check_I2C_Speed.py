#Check_I2C_Speed.py

def check_i2c_speed_config():
    try:
        with open('/boot/firmware/config.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                if 'dtparam=i2c_arm_baudrate' in line:
                    print(line.strip())
                    if '400000' in line:
                        print("I2C is set to 400kHz in /boot/firmware/config.txt.")
                    else:
                        print("I2C is set to a different speed in /boot/firmware/config.txt.")
                    return
            print("I2C speed setting not found in /boot/firmware/config.txt.")
    except Exception as e:
        print(f"Error reading /boot/firmware/config.txt: {e}")

check_i2c_speed_config()
