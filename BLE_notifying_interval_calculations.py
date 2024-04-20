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
            print("Notification", count + 1, "- instant_speed:", data[0], "| total_distance:", data[4])
            count += 1

        await client.is_connected()
        trainer = FitnessMachineService(client)
        trainer.set_indoor_bike_data_handler(my_measurement_handler)
        start_time = time.time()
        await trainer.enable_indoor_bike_data_notify()
        await asyncio.sleep(5.0)
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
    device_address = "D8:ED:35:29:B4:C6"
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(device_address))
