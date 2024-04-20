import asyncio
import time
import socket
import math
from bleak import BleakClient
from datetime import datetime
from pycycling_edited.fitness_machine_service import FitnessMachineService

speed = 0
resistance = 0
new_resistance = 0
t_end = 0
t_start = 0
prev_resistance = 0
total_time = 0
count = 0
seq_num = 1
resistance_time = None
checkStart = True
weight = 800
new_power = 0


avg_res = [-0.01, 0.0, 0.0, 0.0, -0.01, -0.01, 0.0, 0.0, -0.01, -0.01, -0.02, 0.09, 0.08, 0.01, 0.0, 
        0.04, -0.05, -0.01, -0.08, 0.13, 0.1, -0.07, -0.02, 0.0, -0.07, -0.07, -0.08, -0.06, -0.04,
        -0.12, -0.05, -0.08, -0.11, -0.08, -0.05, -0.06, -0.02, 0.11, 0.06, -0.1, -0.14, -0.2, 
        -0.18, -0.06, -0.03, -0.07, -0.07, -0.11, -0.12, -0.16, -0.21, -0.19, -0.09, -0.11, -0.16,
        -0.13, -0.25, -0.18, -0.24, -0.38, -0.38, -0.09, -0.07, -0.18, -0.15, -0.03, -0.25, -0.09,
        -0.1, -0.04, 0.05, 0.0, 0.13, -0.02, -0.03, 0.03, 0.0, 0.13, 0.12, 0.09, 0.06, 0.02, 0.12, 
        0.07, 0.11, 0.1, 0.26, 0.18, 0.22, 0.02, 0.02, 0.06, 0.02, -0.02, -0.04, -0.04, -0.1, -0.09,
        -0.05, -0.04, -0.09, -0.07, -0.16, 0.02, -0.06, -0.19, -0.12, -0.01, -0.02, -0.02, -0.02, 0.03,
        0.08, -0.01, 0.06, -0.05, 0.01, 0.0, 0.01, -0.03, -0.07, 0.06, -0.03, 0.0, -0.1, 0.02, -0.04, 
        -0.01, -0.01, -0.03, 0.03, -0.03, -0.15, -0.04, 0.04, -0.05, -0.01, 0.05, -0.1, -0.02, 0.06, 
        0.27, -0.07, -0.01, -0.04, -0.01, 0.03, 0.03, 0.15, 0.06, 0.04, 0.02, 0.01, 0.03, -0.03, 0.06, 
        0.03, 0.04, 0.07, 0.15, -0.06, 0.0, 0.13, 0.09, 0.02, -0.07, -0.03, 0.01, -0.04, -0.04, -0.08, 
        -0.18, 0.1, -0.06, 0.13, 0.03, 0.02, -0.01, 0.01, 0.04, -0.01, 0.08, 0.01, 0.1, 0.17, 0.0, 0.02, 
        -0.05, -0.02, -0.03, 0.03, -0.02, 0.04, 0.01, -0.03, -0.03, 0.03, -0.15, -0.06, 0.02, 0.14, -0.04, 
        0.02, 0.1, 0.04, 0.06, 0.06, 0.03, -0.01, 0.05, 0.1, 0.08, 0.06, 0.08, 0.04, 0.02, 0.09, 0.07, 0.11, 
        0.05, 0.07, 0.01, 0.0, 0.12, 0.01, 0.04, 0.03, 0.08, 0.08, 0.1, 0.09, 0.05, 0.07, 0.16, 0.13, 0.14, 
        0.12, 0.07, 0.13, 0.1, 0.04, 0.13, 0.12, 0.09, 0.07, 0.14, 0.13, 0.11, 0.11, 0.1, 0.1, 0.11, 0.13, 
        0.07, 0.11, 0.04, 0.06, 0.1, 0.07, 0.0, 0.16, -0.02, 0.02, 0.04, 0.01, 0.01, 0.04, 0.01, 0.0, 0.05, 
        0.06, 0.0, 0.0, 0.0, 0.02, 0.03, -0.03, 0.0, 0.02, -0.01, -0.01, 0.01, -0.01, -0.01, 0.0, 0.1, -0.02, 
        -0.07, -0.1, -0.01, -0.01, -0.05, -0.06, -0.04, -0.04, 0.01, -0.02, -0.02, 0.0, 0.02, 0.05, -0.07, 0.02, 
        0.0, 0.0, 0.12, 0.02, 0.05, 0.03, 0.05, 0.0, 0.09, 0.05, 0.12, 0.09, 0.09, 0.1, 0.09, 0.03, 0.1, 0.01, 0.01]



async def run(address):
    async with BleakClient(address) as client:
        speed_data = []
        client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_ip = "65.0.76.120" # replace with server ip
        server_port = 5500
        client_udp.bind(('0.0.0.0', 5400))
        name = "p1"
   
       #change on_message
        '''def on_message(client, userdata, msg):
            global resistance_time
            global received_message_topic2
            global t_end
            if msg.topic == "VRcycling/UserA/IncTime":
                resistance_time = msg.payload.decode()
                #print("Time Duration for Increasing Resistance:", resistance_time)
            elif msg.topic == "VRcycling/UserA/Delay":
                received_message_topic2 = msg.payload.decode()
                t_end = time.time()'''
        def udp_send(client_socket, message, id):
            send_bytes = f"R:{id}:{message}".encode('ascii')
            print(f"R:{id}:{message}")
            client_socket.send(send_bytes)

        def udp_client_ready(client_socket,id):
            send_bytes = f"R:{id}:ready".encode('ascii')
            client_socket.send(send_bytes)
        
        def udp_client_createGame(client_socket):
            send_bytes = f"create a game room".encode('ascii')
            client_socket.send(send_bytes)


        def udp_receive(client_socket):
            #print("waiting for message to receive")
            receive_bytes, _ = client_socket.recvfrom(1024)
            received_string = receive_bytes.decode('ascii')
            print("Message received from the server: " + received_string)
            return received_string 
                
        def my_measurement_handler(data):
            global speed
            global video_time
            global t_start
            global message
            global resistance_time
            global client_type
            global id_name
            global seq_num
            global seq_numOculus
            global checkStart
            global new_resistance
            global prev_resistance
            global resistance
            eps = 1e-10
            speed = data[0]
            power = data[6]
            distance = data[4]
            resistance = power/(speed + eps)
            checkStart = True
            
            #print(datetime.now(), "Speed:", data[0], "Distance:", data[4], "Power:", data[6], "Resistance:", resistance)
            #print("Time when speed data came:", t_start, 'speed =', speed)
            #client_mqtt.publish("VRcycling/UserA/Speed", str(data[0])) #publish
            #client_mqtt.publish("VRcycling/UserA/Distance", str(data[4])) #publish

            message = f"{seq_num}:{speed}:{distance}"
            seq_num += 1
            t_start = time.time()
            udp_send(client_udp, message, name)
            receiving_string = udp_receive(client_udp)
            
            #print(receiving_string)
            client_type, id_name, seq_numOculus, resistance_time_str, video_time = receiving_string.split(":")
            resistance_time = int(resistance_time_str)
                     

            '''client_mqtt.subscribe("VRcycling/UserA/IncTime") #subscribe
            client_mqtt.subscribe("VRcycling/UserA/Delay") #subscribe
            # Set the callback function for when a message is received
            client_mqtt.on_message = on_message'''

            
            #print(weight)
            global new_power
            global new_resistance
            global prev_resistance
            new_resistance = avg_res[resistance_time] # mg[sinx]
            print("in_1")
            #new_resistance = 0 #change
            if (resistance_time):
                print("in_2")
                prev_resistance = new_resistance
                new_power = weight*(math.sin(new_resistance)+0.6*math.cos(new_resistance))*((speed*10)/36)
                print("target power", new_power)
                ftms.set_target_power(new_power)
                    #print(speed*(new_resistance))
                
                if new_power >= 0:
                    ftms.set_target_power(new_power)
                    #print(speed*(new_resistance))
                    
                else:
                    new_power = 0
                    ftms.set_target_power(new_power)
                    #print(speed*(new_resistance))
                    
                
            elif resistance_time == None:
                ftms.set_target_power(0)
                
            else:
                ftms.set_target_power(new_power)
                #print(speed*(new_resistance))
                
            
        def print_control_point_response(message):
            #print("Received control point response:")
            #print(message)
            print()
        try:

            await client.is_connected()


            client_udp.connect((server_ip, server_port))
            #udp_client_createGame(client_udp)
            
            udp_client_ready(client_udp,name)
            
            startMsg = udp_receive(client_udp)
            print("this msg is", startMsg)
            #check if start message received
            if (startMsg == "Start"): 
                global weight    
                print("Start received")
                ftms = FitnessMachineService(client)
                ftms.set_indoor_bike_data_handler(my_measurement_handler)
                #print("message is", message)
                
                await ftms.enable_indoor_bike_data_notify()
                ftms.set_control_point_response_handler(print_control_point_response)
                await ftms.enable_control_point_indicate()
                
                await ftms.request_control()
                print(weight)
                #prev_resistance = 0

                
                await ftms.set_target_power(0)
                await asyncio.sleep(500)
            
        except asyncio.CancelledError:
            print("CancelledError received. Disconnecting...")
            
        finally:
            await client.disconnect()  # Disconnect from BLE client
            

        with open('speed_data.csv', 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerows(speed_data)
        


if __name__ == "__main__":
    import os
    import csv
    
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    #device_address = "D8:87:6C:82:51:0D"
    device_address = "D5:6A:1A:46:93:4B"
    #device_address = "D8:ED:35:29:B4:C6" 
    
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

