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

# broker_address = "test.mosquitto.org" #external broker
# client_mqtt = mqtt.Client("10.10.14.3") #create new instance
# client_mqtt.connect(broker_address) #connect to broker

broker_address = "18.140.19.253"
port = 8090
username = "bikeuser"
password = "DYuKE42w8CoSDyb0HN46Blkk9XSfY8Z9zes6Ek6eA"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
    else:
        print("Failed to connect, return code %d\n", rc)

def on_disconnect(client, userdata, rc):
    print("Disconnected from MQTT Broker!")

client_mqtt = mqtt.Client()

client_mqtt.on_connect = on_connect
client_mqtt.on_disconnect = on_disconnect

client_mqtt.username_pw_set(username, password)

client_mqtt.connect(broker_address, port)

speed = 0
resistance = 0
new_resistance = 0
received_message_topic1 = None
prev_resistance = 0
code_running = False

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s', filename='logfile2.log')

#res_dic = {'1': 0.5 , '20': 5 , '52': 0.5 , '54': -4, '73': 1.4  , '84': -1.3 , '90': -5, '93': 3.3,
#           '104': -0.4, '109':-3.1, '113': 3.3, '137':-3.2,'142': 0.95, '145': -1.3, '149': -2.2,
#           '154':-3.1, '163':-4, '172': 3.4, '174': 0.5, '179':-4, '191':2.4, '196':0.5, '220':-3.2,
#           '227':1.4, '230':-0.4, '240':0.5, '252':-1.05, '258':0.95, '261':-1.05, '270':0.5,
#           '293':5, '317':0.5, '326':-3.55}    # Trip2

#res_dic =  {"0":0.5, "27":-1, "33":0.5, "43":2, "56":3, "83":1, "98":2, "106":1, "110":0.5,
#             "113":-1, "119":-2, "129":1, "141":0.5, "145":-1, "151":-2, "159":0.5, "176":-1,
#               "192":1, "215":0.5, "226":-1, "236":0.5, "240":-2, "246":-3, "249":-5, "256":-2, 
#               "261":0.5, "263":1, "268":3, "275":2, "299":1, "311":2, "339":1, "347":-1, "348":-3,
#                 "353":-4, "356":2,"358":1} #Nuwara Eliya trip

#res_dic = {'0': -0.5, '1': -0.5, '2': -0.5, '23': 1.0, '24': 1.0, '25': 1.0, '26':-0.5, '28':-1, '29':-1, '30':-1, '41': -1.0, '42': -1.0, '43': -1.0, '60': -2.0, '61': -2.0, '62': -2.0, '79': -2.5, '80': -2.5, '81': -2.5, '91': -1.0, '92': -1.0, '93': -1.0, '107': -0.5, '108': -0.5, '109': -0.5, '117': 1.0, '118': 1.0, '119': 1.0, '129': -1.0, '130': -1.0, '131': -1.0, '137': -0.5, '138': -0.5, '139': -0.5, '145': -1.5, '146': -1.5, '147': -1.5, '157': -0.5, '158': -0.5, '159': -0.5, '173': 1.0, '174': 1.0, '175': 1.0, '191': -1.0, '192': -1.0, '193': -1.0, '205': -1.5, '206': -1.5, '207': -1.5, '217': -2.0, '218': -2.0, '219': -2.0, '223': -0.5, '224': -0.5, '225': -0.5, '233': 1.0, '234': 1.0, '235': 1.0, '240': 1.5, '241': 1.5, '242': 1.5, '248': 2.0, '249': 2.0, '250': 2.0, '257': -0.5, '258': -0.5, '259': -0.5, '261': -1.0, '262': -1.0, '263': -1.0, '287': -1.5, '288': -1.5, '289': 1.5, '299': -0.5, '300': -0.5, '301': -0.5, '310': -1.0, '311': -1.0, '312': -1.0, '323': -2.0, '324': -2.0, '325': -2.0, '335': -1.0, '336': -1.0, '337': -1.0, '342': -0.5, '343': -0.5, '344': -0.5, '346': 1.0, '347': 1.0, '348': 1.0, '353': 1.5, '354': 1.5, '355': 1.5, '357': -0.5}
#res_dic = {'0': 0.5, '1': 0.5, '2': 0.5, '23': -1.0, '24': -1.0, '25': -1.0, '26':0.5, '28':1, '29':1, '30':1, '41': 1.0, '42': 1.0, '43': 1.0, '60': 2.0, '61': 2.0, '62': 2.0, '79': 2.5, '80': 2.5, '81': 2.5, '91': 1.0, '92': 1.0, '93': 1.0, '107': 0.5, '108': 0.5, '109': 0.5, '117': -1.0, '118': -1.0, '119': -1.0, '129': 1.0, '130': 1.0, '131': 1.0, '137': 0.5, '138': 0.5, '139': 0.5, '145': 1.5, '146': 1.5, '147': 1.5, '157': 0.5, '158': 0.5, '159': 0.5, '173': -1.0, '174': -1.0, '175': -1.0, '191': 1.0, '192': 1.0, '193': 1.0, '205': 1.5, '206': 1.5, '207': 1.5, '217': 2.0, '218': 2.0, '219': 2.0, '223': 0.5, '224': 0.5, '225': 0.5, '233': -1.0, '234': -1.0, '235': -1.0, '240': -1.5, '241': -1.5, '242': -1.5, '248': -2.0, '249': -2.0, '250': -2.0, '257': 0.5, '258': 0.5, '259': 0.5, '261': 1.0, '262': 1.0, '263': 1.0, '287': 1.5, '288': 1.5, '289': 1.5, '299': 0.5, '300': 0.5, '301': 0.5, '310': 1.0, '311': 1.0, '312': 1.0, '323': 2.0, '324': 2.0, '325': 2.0, '335': 1.0, '336': 1.0, '337': 1.0, '342': 0.5, '343': 0.5, '344': 0.5, '346': -1.0, '347': -1.0, '348': -1.0, '353': -1.5, '354': -1.5, '355': -1.5, '357': 0.5}
#res_dic = {'1': 0.5, '23': -1.0,'26':0.5, '28':1, '41': 1.0, '60': 2.0, '79': 2.5, '91': 1.0, '107': 0.5, '117': -1.0, '129': 1.0, '137': 0.5, '145': 1.5, '157': 0.5, '173': -1.0, '191': 1.0, '205': 1.5, '217': 2.0, '223': 0.5, '233': -1.0, '240': -1.5, '248': -2.0, '257': 0.5, '261': 1.0, '287': 1.5, '299': 0.5, '310': 1.0, '323': 2.0, '335': 1.0,  '342': 0.5,  '346': -1.0,'353': -1.5, '357': 0.5}
res_dic = {'1': 0.5,'26':-1,'41': 1.8,'60': 2.0,'79': -1,'113': -2.0, '137': 0.5, '145': -2, '173': -2, '191': 0.5, '220': -1, '235': -2,'240': -2, '248': -2.0, '254': 1, '261': 1.5,'287': 1.8,'299': 0.5,'310': 1.0, '311': 1.0, '312': 1.0, '323': 2.0, '324': 2.0, '325': 2.0, '335': 1.0, '336': 1.0, '337': 1.0, '342': 0.5, '343': 0.5, '344': 0.5, '346': -1.0, '347': -1.0, '348': -1.0, '353': -1.5, '354': -1.5, '355': -1.5, '357': 0.5}
#res_dic = {'0': -0.5, '23': 1.0, '26':-0.5, '28':-1, '41': -1.0, '60': -2.0, '79': -2.5, '91': -1.0, '107': -0.5, '117': 1.0, '129': -1.0, '137': -0.5, '145': -1.5, '157': -0.5, '173': 1.0, '191': -1.0, '205': -1.5, '217': -2.0, '223': -0.5, '233': 1.0, '240': 1.5, '248': 2.0, '257': -0.5, '261': -1.0, '287': -1.5, '299': -0.5, '310': -1.0, '323': -2.0, '335': -1.0, '342': -0.5, '346': 1.0, '353': -1.5, '357': -0.5}

async def run(address):
    async with BleakClient(address) as client:
        global new_resistance
        def on_message(client, userdata, msg):
            global received_message_topic1
            if msg.topic == "VRcycling/UserA/IncTime":
                received_message_topic1 = msg.payload.decode()
                print("Received message from oculus, time",received_message_topic1)
                #print("Time Duration for Increasing Resistance:", received_message_topic1)
                
        def my_measurement_handler(data):
            global speed
            global resistance
            switch_state = GPIO.input(switch_pin)
            eps = 1e-10
            speed = data[0]
            power = data[6]
            #if (speed + eps !=0):
            #    resistance = power/(speed + eps)
            #else:
            #    resistance = power/speed
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
                print("in to the loop")
                #print("Received from oculus",received_message_topic1)
                if ((received_message_topic1 in res_dic.keys()) and (prev_resistance != received_message_topic1)):
                    prev_resistance = received_message_topic1
                    print('inside:when resistance change happen')
                    logging.info('inside')
                    new_resistance = res_dic[received_message_topic1] + resistance
                    print("New Resistance calculated",new_resistance)
                    if new_resistance >= 0:
                        await ftms.set_target_power(speed*(new_resistance))
                        print("New writing power",speed*(new_resistance))
                        await asyncio.sleep(1)
                    else:
                        new_resistance = 0 
                        await ftms.set_target_power(speed*(new_resistance))
                        print("New writing power",speed*(new_resistance))
                        await asyncio.sleep(1)

                elif received_message_topic1 == None:
                    await ftms.set_target_power(0)
                    await asyncio.sleep(2)
                else:
                    await ftms.set_target_power(speed*(new_resistance))
                    print("New writing power",speed*(new_resistance))
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
    
