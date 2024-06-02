import asyncio
import time
import socket
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

res_dic = {'1': 0.5 , '20': 5 , '52': 0.5 , '54': -4, '73': 1.4  , '84': -1.3 , '90': -5, '93': 3.3,
           '104': -0.4, '109':-3.1, '113': 3.3, '137':-3.2,'142': 0.95, '145': -1.3, '149': -2.2,
           '154':-3.1, '163':-4, '172': 3.4, '174': 0.5, '179':-4, '191':2.4, '196':0.5, '220':-3.2,
           '227':1.4, '230':-0.4, '240':0.5, '252':-1.05, '258':0.95, '261':-1.05, '270':0.5,
           '293':5, '317':0.5, '326':-3.55}

async def run(address):
    async with BleakClient(address) as client:
        speed_data = []
        client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_ip = "65.0.76.120" # replace with server ip
        server_port = 5500
        client_udp.bind(('0.0.0.0', 5400))
        name = "ndl"
   
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
            client_socket.send(send_bytes)

        def udp_client_ready(client_socket,id):
            send_bytes = f"R:{id}:ready".encode('ascii')
            client_socket.send(send_bytes)
        
        def udp_client_createGame(client_socket):
            send_bytes = f"create a game room".encode('ascii')
            client_socket.send(send_bytes)


        def udp_receive(client_socket):
            print("waiting for message to receive")
            receive_bytes, _ = client_socket.recvfrom(1024)
            received_string = receive_bytes.decode('ascii')
            #print("Message received from the server: " + received_string)
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
            print(receiving_string)
            client_type, id_name, seq_numOculus, resistance_time, video_time = receiving_string.split(":")
        
                     

            '''client_mqtt.subscribe("VRcycling/UserA/IncTime") #subscribe
            client_mqtt.subscribe("VRcycling/UserA/Delay") #subscribe
            # Set the callback function for when a message is received
            client_mqtt.on_message = on_message'''
            
        def print_control_point_response(message):
            #print("Received control point response:")
            #print(message)
            print()

        try:

            await client.is_connected()


            client_udp.connect((server_ip, server_port))
            udp_client_ready(client_udp,name)
            #udp_client_createGame(client_udp)

            
            Msg = udp_receive(client_udp)
            if (Msg == "game created"):
                print("game created received")
                udp_client_ready(client_udp,name)
                startMsg = udp_receive(client_udp)
            print("this msg is", startMsg)
            #check if start message received
            if (startMsg == "Start"):     
                print("Start received")
                ftms = FitnessMachineService(client)
                ftms.set_indoor_bike_data_handler(my_measurement_handler)
                #print("message is", message)
                
                await ftms.enable_indoor_bike_data_notify()
                ftms.set_control_point_response_handler(print_control_point_response)
                await ftms.enable_control_point_indicate()
                
                await ftms.request_control()
                
                #prev_resistance = 0
                for i in range(300):
                    global new_resistance
                    speed_data.append(['start', t_start, speed])
                    #print(resistance_time)
                    #new_resistance = 0 #change
                    if ((resistance_time in res_dic.keys()) and (prev_resistance != resistance_time)):
                        prev_resistance = resistance_time
                        new_resistance = res_dic[resistance_time] + resistance
                        #print(new_resistance)
                        if new_resistance >= 0:
                            await ftms.set_target_power(speed*(new_resistance))
                            #print(speed*(new_resistance))
                            await asyncio.sleep(1)
                        else:
                            new_resistance = 0
                            await ftms.set_target_power(speed*(new_resistance))
                            #print(speed*(new_resistance))
                            await asyncio.sleep(1)

                    elif resistance_time == None:
                        await ftms.set_target_power(0)
                        await asyncio.sleep(1)
                    else:
                        await ftms.set_target_power(speed*(new_resistance))
                        #print(speed*(new_resistance))
                        await asyncio.sleep(1)
                
                await ftms.set_target_power(0)
                await asyncio.sleep(5)
            
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

