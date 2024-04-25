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
prev_resistance = None
total_time = 0
count = 0
seq_num = 1
resistance_time = 0
checkStart = True
weight = 400
new_power = 0
next_elevation = 0
prev_elevation = None

avg_res = [0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -3.0, -1.169, -1.169, -1.169, -1.169, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 0.577, 0.577, 0.577, 0.577, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, -1.169, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 1.413, 1.413, 1.413, 1.413, 1.413, 1.413, 2.221, 2.221, 2.221, 2.221, 2.221, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 2.221, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, -0.285, -0.285, -0.285, -0.285, -0.285, -0.285, -0.285, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577, 0.577]

print(len(avg_res))
async def run(address):
    async with BleakClient(address) as client:
        speed_data = []
        client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_ip = "65.0.76.120" # replace with server ip
        server_port = 5500
        client_udp.bind(('0.0.0.0', 5400))
        name = "p1"

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
        def make_socket_non_blocking(sock):
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.setblocking(False)

        make_socket_non_blocking(client_udp)
                
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
            print("speed", speed)
            message = f"{seq_num}:{speed}:{distance}"
            seq_num += 1
            t_start = time.time()
            udp_send(client_udp, message, name)
            receiving_string = udp_receive(client_udp)
            
            #print(receiving_string)
            client_type, id_name, seq_numOculus, resistance_time_str, video_time = receiving_string.split(":")
            resistance_time = int(resistance_time_str)            
            #print(weight)
            global new_power
            global new_resistance
            global prev_resistance
            global next_elevation
            global prev_elevation
            next_elevation = avg_res[resistance_time]

            new_resistance = resistance +  next_elevation # weight*(math.sin(3*avg_res[resistance_time])+0.4*math.cos(3*avg_res[resistance_time]))# mg[sinx]
            print("resistance", resistance, "and new resistance" , new_resistance , )
            print("pre res", prev_resistance, "and res time", resistance_time)
            print("pre elevation", prev_elevation, "and next elevation", next_elevation)
            #new_resistance = 0 #change
            
                    
            print("res",resistance_time)    
            if resistance_time == 0:
                asyncio.ensure_future(ftms.set_target_power(80))

                print()
            elif ((prev_resistance != resistance_time ) and (next_elevation != prev_elevation)):
                print("next elevation", next_elevation)

                prev_elevation = next_elevation
                prev_resistance = resistance_time 

                new_power = new_resistance*10 +20
                new_power = round(new_power, 2)
                print("target power", new_power)
                asyncio.ensure_future(ftms.set_target_power(new_power))
                    #print(speed*(new_resistance))
                
                if new_power >= 0:
                    asyncio.ensure_future(ftms.set_target_power(new_power))
                    #print(speed*(new_resistance))
                    
                else:
                    new_power = 0
                    asyncio.ensure_future(ftms.set_target_power(new_power))
                    #print(speed*(new_resistance))
                
            else:
                asyncio.ensure_future(ftms.set_target_power(new_power))
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

                
                #await ftms.set_target_power()
                await asyncio.sleep(1000)
            
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

