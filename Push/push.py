import RPi.GPIO as GPIO
import subprocess
import os
import time
import bluetooth
import socket
import logging
# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
code_running = False
# Set up GPIO pin for the switch
LED_PIN_BLE = 27
LED_PIN_WIFI = 22
switch_pin = 17
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN_BLE, GPIO.OUT)
GPIO.setup(LED_PIN_WIFI, GPIO.OUT)
ble_state = False
wifi_status = "Not Connected"
onetime = False

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='logfile.log')

def is_bluetooth_on(state):
    try:
        if (state):
            return True
        devices = bluetooth.discover_devices(lookup_names=True)
        return True
    except OSError:
        return False
def is_connected(host="8.8.8.8",port=53,timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.connect((host,port))
        s.close()
        return True
    except Exception as e:
        return False
GPIO.output(LED_PIN_BLE, GPIO.LOW)
GPIO.output(LED_PIN_WIFI, GPIO.LOW)
time.sleep(5)

try:
    
    while True:
        # Check the state of the switch
        switch_state = GPIO.input(switch_pin)
        time.sleep(0.5)
        if switch_state == GPIO.LOW:
            onetime= True# Switch is ON
            print("Switch is ON. Running script...")
            logging.info("Switch is ON. Running script...")
            # Run your Python script here
            subprocess.call(["python", "/home/pi/Desktop/Client/script_with_new_broker.py"])
            code_running = True
        elif switch_state == GPIO.HIGH and onetime:
            print("Switch is off. Keyboard Inturrupt...")
            logging.info("Switch is off. Keyboard Inturrupt...")
            #raise KeyboardInterrupt
        else:# Switch is OFF
            print("Switch is OFF. Exiting script.")
            logging.info("Switch is OFF. Exiting script.")
        
        if (is_bluetooth_on(ble_state)):
            
            ble_state = True
            print("Bluetooth On")
            logging.info("Bluetooth On")
            GPIO.output(LED_PIN_BLE, GPIO.HIGH)
            
                
        else:
            GPIO.output(LED_PIN_BLE, GPIO.LOW)
            print("Bluetooth off")
            logging.info("Bluetooth off")
            
        if is_connected():
            GPIO.output(LED_PIN_WIFI, GPIO.HIGH)
            print("Wifi is connected")
            logging.info("Wifi is connected")
            # Turn on LED
            #time.sleep(0.5)  # LED on for 0.5 seconds
              # LED off for 0.5 seconds
        else:
            GPIO.output(LED_PIN_WIFI, GPIO.LOW)
            print("Wifi is not connected")
            logging.info("Wifi is not connected")
            # Turn off LED
            #time.sleep(0.5)
        
#                 os.system("pkill -f /home/pi/Desktop/Client/script_with_new_broker.py") # Raise a keyboard interrupt to stop the script

except KeyboardInterrupt:
    print("Keyboard interrupt detected. Exiting...")
    logging.info("Keyboard interrupt detected. Exiting...")
    GPIO.cleanup()  # Clean up GPIO on exit
