import asyncio
from bleak import BleakClient

# 设置 Thunderboard 的 MAC 地址
device_mac = "3A2EA375-D3AE-FE8D-23F4-FBD24D65ED06"

async def scan_services_and_characteristics(device_mac):
    try:
        async with BleakClient(device_mac) as client:
            print("Connected to the device.")
            services = await client.get_services()
            print("Scanning for services and characteristics...\n")
            for service in services:
                print(f"Service: {service.uuid}")
                for char in service.characteristics:
                    print(f"  Characteristic: {char.uuid} - Properties: {char.properties}")
    except Exception as e:
        print(f"Error: {e}")

# 主程序入口
if __name__ == "__main__":
    asyncio.run(scan_services_and_characteristics(device_mac))