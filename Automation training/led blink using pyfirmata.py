from pyfirmata2 import Arduino, util
import time

# Replace with your correct COM port or /dev/ttyUSBx (Linux/Mac)
board = Arduino('COM5')  # Example: 'COM3' on Windows, '/dev/ttyUSB0' on Linux

# Define the pin connected to the LED (e.g., Digital Pin 13)
led_pin = board.get_pin('d:13:o')  # d = digital, 13 = pin number, o = output

print("Running LED loop: ON for 5 sec, OFF for 10 sec")

while True:
    led_pin.write(1)  # Turn ON LED
    print("LED ON")
    time.sleep(5)     # Wait for 5 seconds

    led_pin.write(0)  # Turn OFF LED
    print("LED OFF")
    time.sleep(10)    # Wait for 10 seconds
