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
prev_elevation = 0.2
received_string = None

#avg_res = {8: 0.577, 17: -1.169, 41: -3.0, 61: -1.169, 65: 0.577, 76: 2.221, 87: 0.577, 91: -1.169, 107: 0.577, 175: 1.413, 181: 2.221, 186: 0.577, 200: 2.221, 233: 3.0, 259: 0.577, 291: -0.285, 298: 0.577}
avg_res = {0: 0.577, 1: 0.577, 2: 0.577, 3: 0.577, 4: 0.577, 5: 0.577, 6: 0.577, 7: 0.577, 8: 0.577, 9: 0.577, 10: 0.577, 11: 0.577, 12: 0.577, 
           13: 0.577, 14: 0.577, 15: 0.577, 16: 0.577, 17: -1.169, 18: -1.169, 19: -1.169, 20: -1.169, 21: -1.169, 22: -1.169, 23: -1.169, 
           24: -1.169, 25: -1.169, 26: -1.169, 27: -1.169, 28: -1.169, 29: -1.169, 30: -1.169, 31: -1.169, 32: -1.169, 33: -1.169, 34: -1.169, 
           35: -1.169, 36: -1.169, 37: -1.169, 38: -1.169, 39: -1.169, 40: -1.169, 41: -3.0, 42: -3.0, 43: -3.0, 44: -3.0, 45: -3.0, 46: -3.0, 
           47: -3.0, 48: -3.0, 49: -3.0, 50: -3.0, 51: -3.0, 52: -3.0, 53: -3.0, 54: -3.0, 55: -3.0, 56: -3.0, 57: -3.0, 58: -3.0, 59: -3.0, 60: -3.0, 
           61: -1.169, 62: -1.169, 63: -1.169, 64: -1.169, 65: 0.0, 66: 0.0, 67: 0.0, 68: 0.0, 69: 0.577, 70: 0.577, 71: 0.577, 72: 0.577, 
           73: 0.577, 74: 0.577, 75: 0.577, 76: 2.221, 77: 2.221, 78: 2.221, 79: 2.221, 80: 2.221, 81: 2.221, 82: 2.221, 83: 2.221, 84: 2.221, 
           85: 2.221, 86: 2.221, 87: 0.577, 88: 0.577, 89: 0.577, 90: 0.577, 91: -1.169, 92: -1.169, 93: -1.169, 94: -1.169, 95: -1.169, 96: -1.169, 97: -1.169, 98: -1.169, 99: -1.169, 100: -1.169, 101: -1.169, 102: -1.169, 103: -1.169, 104: -1.169, 105: -1.169, 106: -1.169, 107: 0.577, 108: 0.577, 109: 0.577, 110: 0.577, 111: 0.577, 112: 0.577, 113: 0.577, 114: 0.577, 115: 0.577, 116: 0.577, 117: 0.577, 118: 0.577, 119: 0.577, 120: 0.577, 121: 0.577, 122: 0.577, 123: 0.577, 124: 0.577, 125: 0.577, 126: 0.577, 127: 0.577, 128: 0.577, 129: 0.577, 130: 0.577, 131: 0.577, 132: 0.577, 133: 0.577, 134: 0.577, 135: 0.577, 136: 0.577, 137: 0.577, 138: 0.577, 139: 0.577, 140: 0.577, 141: 0.577, 142: 0.577, 143: 0.577, 144: 0.577, 145: 0.577, 146: 0.577, 147: 0.577, 148: 0.577, 149: 0.577, 150: 0.577, 151: 0.577, 152: 0.577, 153: 0.577, 154: 0.577, 155: 0.577, 156: 0.577, 157: 0.577, 158: 0.577, 159: 0.577, 160: 0.577, 161: 0.577, 162: 0.577, 163: 0.577, 164: 0.577, 165: 0.577, 166: 0.577, 167: 0.577, 168: 0.577, 169: 0.577, 170: 0.577, 171: 0.577, 172: 0.577, 173: 0.577, 174: 0.577, 175: 1.413, 176: 1.413, 177: 1.413, 178: 1.413, 179: 1.413, 180: 1.413, 181: 2.221, 182: 2.221, 183: 2.221, 184: 2.221, 185: 2.221, 186: 0.577, 187: 0.577, 188: 0.577, 189: 0.577, 190: 0.577, 191: 0.577, 192: 0.577, 193: 0.577, 194: 0.577, 195: 0.577, 196: 0.577, 197: 0.577, 198: 0.577, 199: 0.577, 200: 2.221, 201: 2.221, 202: 2.221, 203: 2.221, 204: 2.221, 205: 2.221, 206: 2.221, 207: 2.221, 208: 2.221, 209: 2.221, 210: 2.221, 211: 2.221, 212: 2.221, 213: 2.221, 214: 2.221, 215: 2.221, 216: 2.221, 217: 2.221, 218: 2.221, 219: 2.221, 220: 2.221, 221: 2.221, 222: 2.221, 223: 2.221, 224: 2.221, 225: 2.221, 226: 2.221, 227: 2.221, 228: 2.221, 229: 2.221, 230: 2.221, 231: 2.221, 232: 2.221, 233: 3.0, 234: 3.0, 235: 3.0, 236: 3.0, 237: 3.0, 238: 3.0, 239: 3.0, 240: 3.0, 241: 3.0, 242: 3.0, 243: 3.0, 244: 3.0, 245: 3.0, 246: 3.0, 247: 3.0, 248: 3.0, 249: 3.0, 250: 3.0, 251: 3.0, 252: 3.0, 253: 3.0, 254: 3.0, 255: 3.0, 256: 3.0, 257: 3.0, 258: 3.0, 259: 0.577, 260: 0.577, 261: 0.577, 262: 0.577, 263: 0.577, 264: 0.577, 265: 0.577, 266: 0.577, 267: 0.577, 268: 0.577, 269: 0.577, 270: 0.577, 271: 0.577, 272: 0.577, 273: 0.577, 274: 0.577, 275: 0.577, 276: 0.577, 277: 0.577, 278: 0.577, 279: 0.577, 280: 0.577, 281: 0.577, 282: 0.577, 283: 0.577, 284: 0.577, 285: 0.577, 286: 0.577, 287: 0.577, 288: 0.577, 289: 0.577, 290: 0.577, 291: -0.285, 292: -0.285, 293: -0.285, 294: -0.285, 295: -0.285, 296: -0.285, 297: -0.285, 298: 0.577, 299: 0.577, 300: 0.577, 301: 0.577, 302: 0.577, 303: 0.577, 304: 0.577, 305: 0.577, 306: 0.577, 307: 0.577, 308: 0.577, 309: 0.577, 310: 0.577, 311: 0.577, 312: 0.577, 313: 0.577, 314: 0.577, 315: 0.577, 316: 0.577, 317: 0.577, 318: 0.577, 319: 0.577, 320: 0.577, 321: 0.577}
#avg_res = {8: 0.577, 17: -2.338, 41: -6.0, 61: -2.338,  65: 0.2885, 76: 1.1105, 87: 0.2885, 91: -2.338, 107: 0.2885, 175: 1.1105, 181: 1.1105, 186: 0.2885, 200: 1.5105, 233: 1.7, 259: 0.2885, 291: -0.57, 298:0.2885 }
#avg_res = {8: 0.577, 17: -2.338, 41: -6.0, 61: -2.338,  65: 0.2885, 76: 1.1105, 87: 0.2885, 91: -2.338, 107: 0.2885, 175: 1.1105, 181: 1.1105, 186: 0.2885, 200: 1.1105, 233: 1.5, 259: 0.2885, 291: -0.57, 298:0.2885 }
#avg_res = {8: 0.577, 9: -2.338, 20: -6.0, 30: -2.338, 32: 0.2885, 38: 1.1105, 44: 0.2885, 46: -2.338, 54: 0.2885, 88: 1.1105, 90: 1.1105, 93: 0.2885, 100: 1.5105, 116: 1.5, 130: 0.2885, 146: -0.57, 149: 0.2885}

print(len(avg_res))
async def udp_receive(client_udp, server_ip, server_port):
    global received_string
    print("UDP receive function started.")
    while True:
        try:
            result = await loop.sock_recv(client_udp, 1024)
            
            received_string = result.decode('ascii')
            print("Message received from the server: " + received_string)
            # Process received message as needed
        except asyncio.CancelledError:
            print("UDP receive task cancelled.")
            break
        except Exception as e:
            print(f"Error in UDP receive: {e}")
async def run(address):
    async with BleakClient(address) as client:
        speed_data = []
        client_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_ip = "65.0.76.120" # replace with server ip
        server_port = 5500
        client_udp.bind(('0.0.0.0', 5400))
        name = "Pasindu"

        receive_task = asyncio.create_task(udp_receive(client_udp, server_ip, server_port))


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


        def udp_receive_ready(client_socket):
            #print("waiting for message to receive")
            receive_bytes, _ = client_socket.recvfrom(1024)
            received_string = receive_bytes.decode('ascii')
            print("Message received from the server: " + received_string)
            return received_string 
        
        async def udp_receive2(client_socket):
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
            print("speed", speed)
            print("Power", power)
            print("Resistance", resistance)
            message = f"{seq_num}:{speed}:{distance}"
            seq_num += 1
            t_start = time.time()
            udp_send(client_udp, message, name)

            
            print(received_string)
            client_type, id_name, seq_numOculus, resistance_time_str, video_time, points = received_string.split(":")
            if (resistance_time_str != 'N/A'):
                resistance_time = int(resistance_time_str)            
            #print(weight)
            global new_power
            global new_resistance
            global prev_resistance
            global next_elevation
            global prev_elevation

                
            if resistance_time in avg_res.keys():
                next_elevation = avg_res[resistance_time]

            new_resistance = resistance +  next_elevation # weight*(math.sin(3*avg_res[resistance_time])+0.4*math.cos(3*avg_res[resistance_time]))# mg[sinx]
            print("resistance", resistance, "and new resistance" , new_resistance , )
            print("pre res", prev_resistance, "and res time", resistance_time)
            print("pre elevation", prev_elevation, "and next elevation", next_elevation)
            #new_resistance = 0 #change
            
                    
            print("res",resistance_time)    
            if resistance_time == 0:
                new_power = 80
                asyncio.ensure_future(ftms.set_target_power(80))
                

                print("target power 80", new_power)
           
            #if new_power < power:
            elif ((prev_resistance != resistance_time ) and (next_elevation != prev_elevation)):
                print("next elevation", next_elevation)

                
                prev_resistance = resistance_time 

                #if (next_elevation>0):
                    #new_power = new_resistance*5 + 20
                #else: 
                print("pre elevation", prev_elevation, "and next elevation", next_elevation)
                new_power = power + (next_elevation - prev_elevation)*10
                prev_elevation = next_elevation
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
                    #print(speed*(new_resistance))'''
                
            
                #print(speed*(new_resistance))
            else:
                print("target power", new_power)
                asyncio.ensure_future(ftms.set_target_power(new_power))
                
            
        def print_control_point_response(message):
            #print("Received control point response:")
            #print(message)
            print()
        
        try:

            await client.is_connected()


            client_udp.connect((server_ip, server_port))
            #udp_client_createGame(client_udp)
            
            udp_client_ready(client_udp,name)
            
            startMsg = udp_receive_ready(client_udp)
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
                asyncio.ensure_future(ftms.set_target_power(80))
                print(weight)
                #prev_resistance = 0
                #await udp_receive2(client_udp)

                
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

