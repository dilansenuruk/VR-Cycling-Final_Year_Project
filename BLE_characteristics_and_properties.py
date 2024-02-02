'''This script can search the Bluetooth devices around you and analyse the device
you want, then gives you all the services include in it with the characteristics
and their properties. Not only for classic bluetooth, this script will also work
for the bluetooth low energy.'''

import asyncio
from bleak import BleakScanner, BleakClient

async def discover_devices():
    devices = await BleakScanner.discover()
    return devices

async def get_device_services(device_address):
    async with BleakClient(device_address) as client:
        services = await client.get_services()
    return services

async def main():
    print("Discovering nearby BLE devices...")
    devices = await discover_devices()

    for device in devices:
        name = device.name if device.name else "Unknown"
        if name == "your_bluetooth_device_name": # Include your device name here
            address = device.address
            print(f"\nDevice: {name} ({address})")
        else:
            continue

        services = await get_device_services(address)

        if not services:
            print("No services found for this device.")
        else:
            print("Services:")
            for service in services:
                print(f"\n  Service type: {' '.join(str(service).split(' ')[3:])}")
                print(f"  Service UUID: {service.uuid}")
                print(f"  Characteristics:")
                for char in service.characteristics:
                    print(f"    - {char.uuid}")
                    print(f"            -- {char.properties}")

if __name__ == "__main__":
    import os

    os.environ["PYTHONASYNCIODEBUG"] = str(1)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
