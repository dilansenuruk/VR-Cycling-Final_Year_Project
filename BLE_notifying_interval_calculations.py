import paho.mqtt.client as mqtt
import asyncio
from bleak import BleakClient
from datetime import datetime
import time
from pycycling_edited.fitness_machine_service import FitnessMachineService

broker_address = "test.mosquitto.org" #external broker
client_mqtt = mqtt.Client("10.10.14.3") #create new instance
client_mqtt.connect(broker_address) #connect to broker

count = 0

async def run(address):
    async with BleakClient(address) as client:
        def my_measurement_handler(data):
            global count
            global speed
            global power
            global ins_resistance
            speed = data[0]
            power = data[6]
            eps = 1e-10
            ins_resistance = power/(speed + eps)
            print("Notification", count + 1, "- instant_speed:", data[0], "| total_distance:", data[4])
            new_power = power + 50 
            new_res = ins_resistance + 50/(speed + eps)
            asyncio.ensure_future(trainer.set_target_power(new_power))
            print("instantaneous power",power)
            print("target power", new_power)
            print("instantaneous resistance", ins_resistance)
            print("new resistance", new_res)
            


            count += 1
        def print_control_point_response(message):
            #print("Received control point response:")
            #print(message)
            print()
        await client.is_connected()
        trainer = FitnessMachineService(client)
        trainer.set_indoor_bike_data_handler(my_measurement_handler)
        start_time = time.time()
        await trainer.enable_indoor_bike_data_notify()
        trainer.set_control_point_response_handler(print_control_point_response)
        await trainer.enable_control_point_indicate()
        await trainer.request_control()
        await asyncio.sleep(15)
        asyncio.ensure_future(trainer.set_target_power(50))
        
        await asyncio.sleep(500)
        await trainer.disable_indoor_bike_data_notify()
        end_time = time.time()
        total_time = end_time - start_time
        average_interval = total_time / count
        print("Number of notifications received:", count)
        print(f"Time taken for {count} notifications to be received:", total_time)
        print("Average interval for notifications:", average_interval)

if __name__ == "__main__":
    import os
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    #device_address = "D8:ED:35:29:B4:C6"
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
