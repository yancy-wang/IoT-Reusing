import time
import paramiko
import os
import getpass
import csv
import asyncio
from bleak import BleakClient

# 服务器信息
hostname = '195.148.30.41'  # 服务器的IP地址
username = 'ubuntu'         # 服务器的用户名
private_key_path = '/Users/wangyangyang/.ssh/student-key'  # SSH 私钥的路径
remote_file_path = '/home/ubuntu/ubikampus_compare3/sensor_data.txt'  # 上传到服务器的路径
local_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/data/sensor_data.txt' # 本地保存的文件路径
csv_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/data/transmission_times.csv' # 保存时间的 CSV 文件路径

# 用于存储 10 次 Bluetooth 和 SSH 的传输时间
bluetooth_times = []
ssh_times = []

async def read_sensor_data(device_mac, ssh, sftp):
    global bluetooth_times, ssh_times

    try:
        async with BleakClient(device_mac) as client:
            # 记录蓝牙数据接收时间
            bluetooth_receive_start = time.time()

            # 读取温度数据
            temp_value = await client.read_gatt_char("00002a6e-0000-1000-8000-00805f9b34fb")
            temperature = int.from_bytes(temp_value, byteorder="little") / 100  # 假设温度以摄氏度为单位

            # 读取湿度数据
            humidity_value = await client.read_gatt_char("00002a6f-0000-1000-8000-00805f9b34fb")
            humidity = int.from_bytes(humidity_value, byteorder="little") / 100  # 假设湿度以百分比为单位

            bluetooth_receive_end = time.time()

            # 计算 Bluetooth 传输时间
            bluetooth_transmission_time = bluetooth_receive_end - bluetooth_receive_start
            bluetooth_times.append(bluetooth_transmission_time)
            print(f"Bluetooth transmission time: {bluetooth_transmission_time} seconds")

            # 准备数据并保存到本地文件
            data = {
                "temperature": temperature,
                "humidity": humidity,
                "timestamp": time.time()
            }
            with open(local_file_path, 'w') as file:
                file.write(str(data))

            # 使用 SFTP 上传文件
            upload_start_time = time.time()
            sftp.put(local_file_path, remote_file_path)
            upload_end_time = time.time()

            # 计算 SSH 传输时间
            ssh_transmission_time = upload_end_time - upload_start_time
            ssh_times.append(ssh_transmission_time)
            print(f"SSH transmission time: {ssh_transmission_time} seconds")

    except Exception as e:
        print(f"Error reading from device {device_mac}: {e}")

def save_times_to_csv(bluetooth_times, ssh_times, file_path):
    # 将 10 次的传输时间写入到 CSV 文件
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Attempt', 'Bluetooth Transmission Time (seconds)', 'SSH Transmission Time (seconds)'])
        for i in range(len(bluetooth_times)):
            writer.writerow([i + 1, bluetooth_times[i], ssh_times[i]])

async def main():
    device_mac = "60B1906B-ED70-8BB3-AF3E-046B3E2EEA23"    # Thunderboard MAC 地址

    # 读取解锁私钥所需的 passphrase 并初始化 SSH 连接
    passphrase = getpass.getpass("Enter passphrase for private key: ")

    # 初始化 SSH 和 SFTP 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(private_key_path, password=passphrase)
    ssh.connect(hostname, username=username, pkey=key)
    sftp = ssh.open_sftp()

    try:
        # 运行 10 次读取和传输
        for i in range(10):
            print(f"Iteration {i+1}")
            await read_sensor_data(device_mac, ssh, sftp)
            print(f"Iteration {i+1} completed.\n")

        # 输出 Bluetooth 和 SSH 传输时间的统计结果
        print("\n--- Bluetooth Transmission Times ---")
        for idx, bt_time in enumerate(bluetooth_times):
            print(f"Attempt {idx+1}: {bt_time} seconds")

        print("\n--- SSH Transmission Times ---")
        for idx, ssh_time in enumerate(ssh_times):
            print(f"Attempt {idx+1}: {ssh_time} seconds")

        # 将时间保存到 CSV 文件
        save_times_to_csv(bluetooth_times, ssh_times, csv_file_path)
        print(f"\nTransmission times saved to {csv_file_path}")

    finally:
        # 关闭 SFTP 和 SSH 连接
        sftp.close()
        ssh.close()

if __name__ == "__main__":
    asyncio.run(main())