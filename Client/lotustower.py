# Need the pycycling_edited library in the directory where this script is in.
# before running the script below things have to be done.
#
# upgrade pip ---> pip install --upgrade pip
# install bleak ---> pip install bleak
# install pahe-mqtt ---> pip install paho-mqtt
# install asyncio ---> pip install asyncio
# upgrade bleak pycycling ---> pip install --upgrade bleak pycycling
import time
time.sleep(5)
import asyncio
from bleak import BleakClient
from datetime import datetime
from pycycling_edited.fitness_machine_service import FitnessMachineService
import RPi.GPIO as GPIO
import subprocess
import os
import logging
import paho.mqtt.client as mqtt
# Set up GPIO using BCM numbering
GPIO.setmode(GPIO.BCM)
code_running = False
# Set up GPIO pin for the switch
switch_pin = 17
GPIO.setup(switch_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

broker_address = "test.mosquitto.org" #external broker
client_mqtt = mqtt.Client("10.10.14.3") #create new instance
client_mqtt.connect(broker_address) #connect to broker

speed = 0
resistance = 0
new_resistance = 0
received_message_topic1 = None
prev_resistance = 0
code_running = False

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='logfile2.log')

res_dic = {'1': 0.5 , '20': 5 , '52': 0.5 , '54': -4, '73': 1.4  , '84': -1.3 , '90': -5, '93': 3.3,
           '104': -0.4, '109':-3.1, '113': 3.3, '137':-3.2,'142': 0.95, '145': -1.3, '149': -2.2,
           '154':-3.1, '163':-4, '172': 3.4, '174': 0.5, '179':-4, '191':2.4, '196':0.5, '220':-3.2,
           '227':1.4, '230':-0.4, '240':0.5, '252':-1.05, '258':0.95, '261':-1.05, '270':0.5,
           '293':5, '317':0.5, '326':-3.55}
async def run(address):
    async with BleakClient(address) as client:
        

        def on_message(client, userdata, msg):
            global received_message_topic1
            if msg.topic == "VRcycling/UserA/IncTime":
                received_message_topic1 = msg.payload.decode()
                #print("Time Duration for Increasing Resistance:", received_message_topic1)
                
        def my_measurement_handler(data):
            global speed
            global resistance
            switch_state = GPIO.input(switch_pin)
            eps = 1e-10
            speed = data[0]
            power = data[6]
            resistance = power/(speed + eps)
            print(datetime.now(), "Speed:", data[0], "Distance:", data[4], "Power:", data[6], "Resistance:", resistance)
            client_mqtt.publish("VRcycling/UserA/Speed", str(data[0])) #publish
            client_mqtt.publish("VRcycling/UserA/Distance", str(data[4])) #publish
            client_mqtt.subscribe("VRcycling/UserA/IncTime") #subscribe
            # Set the callback function for when a message is received
            client_mqtt.on_message = on_message
            if (switch_state == GPIO.HIGH and code_running):
                print("Switch low")
                logging.info("Switch low")
                raise KeyboardInterrupt
            
        def print_control_point_response(message):
            '''print("Received control point response:")
            print(message)'''
            print()

        try:
            code_running = True
            await client.is_connected()
            ftms = FitnessMachineService(client)
            ftms.set_indoor_bike_data_handler(my_measurement_handler)
            await ftms.enable_indoor_bike_data_notify()
            ftms.set_control_point_response_handler(print_control_point_response)
            await ftms.enable_control_point_indicate()
            
            await ftms.request_control()
            
            prev_resistance = 0
            for i in range(2000):
                #print("in")
                #print("Received from oculus",received_message_topic1)
                if ((received_message_topic1 in res_dic.keys()) and (prev_resistance != received_message_topic1)):
                    prev_resistance = received_message_topic1
                    print('inside')
                    logging.info('inside')
                    new_resistance = res_dic[received_message_topic1] + resistance
                    print(new_resistance)
                    if new_resistance >= 0:
                        await ftms.set_target_power(speed*(new_resistance))
                        print(speed*(new_resistance))
                        await asyncio.sleep(1)
                    else:
                        new_resistance = 0 
                        await ftms.set_target_power(speed*(new_resistance))
                        print(speed*(new_resistance))
                        await asyncio.sleep(1)

                elif received_message_topic1 == None:
                    await ftms.set_target_power(0)
                    await asyncio.sleep(2)
                else:
                    await ftms.set_target_power(speed*(new_resistance))
                    print(speed*(new_resistance))
                    await asyncio.sleep(1)
            
                
            await ftms.set_target_power(0)
            await asyncio.sleep(5)
            client_mqtt.publish("VRcycling/UserA/Speed", '0')
        except asyncio.CancelledError:
            print("CancelledError received. Disconnecting...")
            logging.info("CancelledError received. Disconnecting...")
            
            client_mqtt.publish("VRcycling/UserA/Speed", '0')
        finally:
            await client.disconnect()  # Disconnect from BLE client
            client_mqtt.loop_stop()
        


if __name__ == "__main__":
    import os
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    #device_address = "D8:87:6C:82:51:0D"
    device_address = "D5:6A:1A:46:93:4B"
    #device_address = "D8:ED:35:29:B4:C6"
    client_mqtt.loop_start()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(run(device_address))
    except KeyboardInterrupt:
        pass
    finally:
        tasks = asyncio.all_tasks(loop=loop)
        for task in tasks:
            task.cancel()

        # Wait for all tasks to be cancelled
        loop.run_until_complete(asyncio.gather(*tasks, return_exceptions=True))

        client_mqtt.disconnect()
        client_mqtt.loop_stop()
    
