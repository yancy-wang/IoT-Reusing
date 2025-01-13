import time
import requests
import pygatt
import paramiko
import os
import getpass
import csv

# SSH 服务器信息
hostname = '195.148.30.41'  # 服务器的IP地址
username = 'ubuntu'         # 服务器的用户名
private_key_path = '/home/pi/.ssh/student-key'  # SSH 私钥的路径
remote_file_path = '/home/ubuntu/ubikampus_compare3/sensor_data.txt'  # 上传到服务器的路径
local_file_path = '/home/pi/mu_code/tbs2data_compare3/sensor_data.txt' # 本地保存的文件路径
csv_file_path = '/home/pi/mu_code/transmission_times.csv' # 保存时间的 CSV 文件路径

# 用于存储 10 次 Bluetooth 和 SSH 的传输时间
bluetooth_times = []
ssh_times = []

def read_sensor_data(device_mac, ssh, sftp):
    global bluetooth_times, ssh_times

    try:
        adapter = pygatt.GATTToolBackend()
        adapter.start()
        device = adapter.connect(device_mac, timeout=15)

        # 记录蓝牙数据接收时间
        bluetooth_receive_start = time.time()

        # 读取数据（假设数据中包含传感器的时间戳）
        temp_value = device.char_read_handle("0x0021")
        bluetooth_receive_end = time.time()

        # 计算 Bluetooth 传输时间
        bluetooth_transmission_time = bluetooth_receive_end - bluetooth_receive_start
        bluetooth_times.append(bluetooth_transmission_time)
        print(f"Bluetooth transmission time: {bluetooth_transmission_time} seconds")

        # 准备数据并保存到本地文件
        data = {
            "temperature": temp,
            "timestamp": time.time()
        }
        with open(local_file_path, 'w') as file:
            file.write(str(data))

        # 使用 SFTP 上传文件
        upload_start_time = time.time()

        # 上传文件
        sftp.put(local_file_path, remote_file_path)

        upload_end_time = time.time()

        # 计算 SSH 传输时间
        ssh_transmission_time = upload_end_time - upload_start_time
        ssh_times.append(ssh_transmission_time)
        print(f"SSH transmission time: {ssh_transmission_time} seconds")

    except Exception as e:
        print(f"Error reading from device {device_mac}: {e}")
    finally:
        if adapter:
            adapter.stop()

def save_times_to_csv(bluetooth_times, ssh_times, file_path):
    # 将 10 次的传输时间写入到 CSV 文件
    with open(file_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        # 写入 CSV 的表头
        writer.writerow(['Attempt', 'Bluetooth Transmission Time (seconds)', 'SSH Transmission Time (seconds)'])
        
        # 写入每次的传输时间
        for i in range(len(bluetooth_times)):
            writer.writerow([i + 1, bluetooth_times[i], ssh_times[i]])

if __name__ == "__main__":
    device_mac = "90:FD:9F:7B:84:67"  # Thunderboard MAC 地址

    # 读取解锁私钥所需的 passphrase 并初始化 SSH 连接
    passphrase = getpass.getpass("Enter passphrase for private key: ")

    # 初始化 SSH 和 SFTP 连接
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    key = paramiko.RSAKey.from_private_key_file(private_key_path, password=passphrase)  # 解锁一次私钥
    ssh.connect(hostname, username=username, pkey=key)
    sftp = ssh.open_sftp()

    try:
        # 运行 10 次读取和传输
        for i in range(10):
            print(f"Iteration {i+1}")
            read_sensor_data(device_mac, ssh, sftp)
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
