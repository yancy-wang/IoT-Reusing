import time
import requests
import csv
import asyncio
from bleak import BleakClient

# 服务器信息
hostname = 'http://195.148.30.41:5000/sensor'  # 服务器的HTTP地址
csv_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_rpi/transmission_times_mac.csv'  # 保存时间的 CSV 文件路径

# 用于存储 1000 次 Bluetooth 和 HTTP 的传输时间
bluetooth_times = []
http_times = []

async def read_sensor_data(device_mac):
    global bluetooth_times, http_times

    try:
        async with BleakClient(device_mac) as client:
            # 记录蓝牙数据接收时间
            bluetooth_receive_start = time.time()

            # 读取温度数据
            temp_value = await client.read_gatt_char("00002a6e-0000-1000-8000-00805f9b34fb")

            bluetooth_receive_end = time.time()

            # 计算 Bluetooth 传输时间
            bluetooth_transmission_time = bluetooth_receive_end - bluetooth_receive_start
            bluetooth_times.append(bluetooth_transmission_time)
            print(f"Bluetooth transmission time: {bluetooth_transmission_time} seconds")

            temperature = int.from_bytes(temp_value, byteorder="little") / 100  # 假设温度以摄氏度为单位
            # 准备 JSON 数据
            data = {
                "temperature": temperature,
                "timestamp": time.time()
            }

            # 使用 HTTP 上传 JSON 数据
            upload_start_time = time.time()
            response = requests.post(hostname, json=data)
            upload_end_time = time.time()

            # 计算 HTTP 传输时间
            if response.status_code == 200:
                http_transmission_time = upload_end_time - upload_start_time
                http_times.append(http_transmission_time)
                print(f"HTTP transmission time: {http_transmission_time} seconds")
            else:
                print(f"Failed to upload data via HTTP, status code: {response.status_code}")

    except Exception as e:
        print(f"Error reading from device {device_mac}: {e}")

def save_times_to_csv(bluetooth_times, http_times, file_path):
    # 将 1000 次的传输时间写入到 CSV 文件
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Attempt', 'Bluetooth Transmission Time (seconds)', 'HTTP Transmission Time (seconds)'])
        for i in range(len(bluetooth_times)):
            writer.writerow([i + 1, bluetooth_times[i], http_times[i]])

async def main():
    device_mac = "3A2EA375-D3AE-FE8D-23F4-FBD24D65ED06"    # Thunderboard MAC 地址

    # 运行 1000 次读取和传输
    for i in range(1000):
        print(f"Iteration {i+1}")
        await read_sensor_data(device_mac)
        print(f"Iteration {i+1} completed.\n")

    # 将时间保存到 CSV 文件
    save_times_to_csv(bluetooth_times, http_times, csv_file_path)
    print(f"\nTransmission times saved to {csv_file_path}")

if __name__ == "__main__":
    asyncio.run(main())