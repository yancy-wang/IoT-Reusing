import os
import time
import paramiko
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import getpass
import serial
import pandas as pd
from datetime import datetime, timedelta

# SSH and file paths setup
HOST = '195.148.30.41'  # Replace with your cPouta IP address
USERNAME = 'ubuntu'  # Replace with your cPouta username
PRIVATE_KEY = '/Users/wangyangyang/.ssh/student-key'
LOCAL_DIRECTORY = '/Users/wangyangyang/Desktop/Finland/summer_job/wio/comparision_THS'  # Local directory path to sync
REMOTE_DIRECTORY = '/home/ubuntu/ubikampus_wio/test0'  # Remote directory path on cPouta

# Serial port setup for Mac (modify for Windows as needed)
ser = serial.Serial('/dev/cu.usbmodem2101', 115200)

# Data lists for storing sensor readings
data_list = []
pm25_data_list = []

# Start time for saving files
start_time = datetime.now()

# SFTP handler to upload files to remote server
class DataHandler(FileSystemEventHandler):
    def __init__(self, client, passphrase):
        super().__init__()
        self.client = client
        self.passphrase = passphrase

    def upload_file(self, local_file_path):
        try:
            transport = paramiko.Transport((HOST, 22))
            transport.connect(username=USERNAME, pkey=paramiko.RSAKey.from_private_key_file(PRIVATE_KEY, password=self.passphrase))
            sftp = paramiko.SFTPClient.from_transport(transport)
            remote_file_path = os.path.join(REMOTE_DIRECTORY, os.path.basename(local_file_path))
            sftp.put(local_file_path, remote_file_path)
            print(f"Uploaded {local_file_path} to cPouta at {remote_file_path}")
            sftp.close()
            transport.close()
        except Exception as e:
            print(f"Error uploading file to cPouta: {e}")

# Function to save data to CSV
def save_to_csv():
    csv_file = os.path.join(LOCAL_DIRECTORY, f'Normal_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv')
    df = pd.DataFrame(data_list, columns=['Timestamp', 'Temperature', 'Humidity', 'Sound', 'Light', "VOCs", "PIR"])
    df.to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")
    return csv_file

def save_pm25_to_csv():
    csv_file = os.path.join(LOCAL_DIRECTORY, f'PM25_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv')
    pm25_df = pd.DataFrame(pm25_data_list, columns=['Timestamp', 'PM2.5'])
    pm25_df.to_csv(csv_file, index=False)
    print(f"PM2.5 data saved to {csv_file}")
    return csv_file

if __name__ == "__main__":
    passphrase = getpass.getpass("Enter passphrase for private key: ")

    observer = Observer()
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    event_handler = DataHandler(client, passphrase)
    observer.schedule(event_handler, LOCAL_DIRECTORY, recursive=True)
    observer.start()

    print(f"Data streaming started. Watching for new files in {LOCAL_DIRECTORY}...")

    try:
        while True:
            # Reading data from serial port
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8').strip()
                
                # Check for PM2.5 data
                if line.startswith("PM2.5="):
                    pm25_value = float(line.split('=')[1])
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    pm25_data_list.append([timestamp, pm25_value])
                    print(f"PM2.5: {pm25_value} at {timestamp}")
                else:
                    # Split sensor data
                    data = line.split(',')
                    if len(data) == 6:
                        temperature = float(data[0])
                        humidity = float(data[1])
                        sound = int(data[2])
                        light = int(data[3])
                        vocs = int(data[4])
                        pir = int(data[5])

                        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        data_list.append([timestamp, temperature, humidity, sound, light, vocs, pir])
                        print(f"Temp: {temperature}, Humidity: {humidity}, Sound: {sound}, Light:{light}, VOCs:{vocs}, PIR:{pir}")

            # Save data and upload CSV every hour (or set interval)
            if datetime.now() - start_time >= timedelta(minutes=1):
                csv_file = save_to_csv()
                pm25_csv_file = save_pm25_to_csv()

                # Upload the CSV files to the remote server
                event_handler.upload_file(csv_file)
                event_handler.upload_file(pm25_csv_file)

                # Clear lists and reset timer
                data_list.clear()
                pm25_data_list.clear()
                start_time = datetime.now()

            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        client.close()

    observer.join()
