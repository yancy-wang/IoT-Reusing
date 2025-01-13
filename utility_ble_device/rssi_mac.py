import asyncio
from bleak import BleakScanner

async def scan_and_get_rssi():
    devices = await BleakScanner.discover()  # Scanning for nearby devices
    for device in devices:
        print(f"Device: {device.name}, Address: {device.address}, RSSI: {device.rssi} dBm")

if __name__ == "__main__":
    asyncio.run(scan_and_get_rssi())