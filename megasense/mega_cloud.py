import time
import binascii
import struct
import asyncio
from datetime import datetime, timedelta
from bleak import BleakClient
import os
import paramiko
import pandas as pd
import getpass
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up the SSH connection info
HOST = '195.148.30.41'
USERNAME = 'ubuntu'
PRIVATE_KEY = '/Users/wangyangyang/.ssh/student-key'
LOCAL_DIRECTORY = '/Users/wangyangyang/Desktop/Finland/summer_job/Mega/mega_sensor/classroom/t1'
REMOTE_DIRECTORY = '/home/ubuntu/ai_sensor/home_kitchen/t1'

# Specify columns to save
columns_to_save = [
    'time', 'co_ppm', 'no2_ppb', 'nc_0p5_npcm3', 'nc_1p0_npcm3', 
    'nc_2p5_npcm3', 'nc_4p0_npcm3', 'nc_10p0_npcm3', 'Mc_1p0_ugpm3', 
    'Mc_2p5_ugpm3', 'Mc_4p0_ugpm3', 'Mc_10p0_ugpm3', 'ozone_ppm'
]

# Upload handler
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

# Function to save data to CSV and clean up
def save_to_csv(data_list):
    csv_file = os.path.join(LOCAL_DIRECTORY, f'Normal_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv')
    df = pd.DataFrame(data_list)
    
    # Select only the columns to save and clean up tuple-like data
    for col in columns_to_save:
        if col in df.columns and col != 'time':
            df[col] = df[col].astype(str).str.replace(r"[()]", "", regex=True).astype(float)
    
    # Save cleaned data to CSV
    df[columns_to_save].to_csv(csv_file, index=False)
    print(f"Data saved to {csv_file}")
    return csv_file

# Unpacking functions
def unpack_bme(byte_value):
    retdict = {}
    bme_temperature = byte_value[0:8]
    temperature = int.from_bytes(bytes.fromhex(bme_temperature), byteorder='little') / 100
    retdict["temperature_c"] = temperature
    bme_humidity = byte_value[8:16]
    humidity = int.from_bytes(bytes.fromhex(bme_humidity), byteorder='little') / 1000
    retdict["humidity_prcnt"] = humidity
    bme_pressure = byte_value[16:24]
    pressure = int.from_bytes(bytes.fromhex(bme_pressure), byteorder='little') / 10000
    retdict["pressure_hpa"] = pressure
    return retdict

def unpack_speco3(byte_value):
    retdict = {}
    spe_ozone = byte_value[0:8]
    ozone = int.from_bytes(bytes.fromhex(spe_ozone), byteorder='little')
    retdict["ozone_ppm"] = ozone
    return retdict

def unpack_mic(byte_value):
    retdict = {}
    mic_eq = byte_value[0:8]
    eq = struct.unpack('<f', bytes.fromhex(mic_eq))[0]
    retdict["eq_db"] = eq
    return retdict

def unpack_mics(byte_value):
    retdict = {}
    mics_co = byte_value[0:4]
    co = int.from_bytes(bytes.fromhex(mics_co), byteorder='little')
    retdict["co_ppm"] = co
    mics_no2 = byte_value[4:8]
    no2 = int.from_bytes(bytes.fromhex(mics_no2), byteorder='little')
    retdict["no2_ppb"] = no2
    return retdict

def unpack_sps(byte_value):
    retdict = {}
    sps_nc0p5 = byte_value[0:8]
    nc0p5 = struct.unpack('<f', bytes.fromhex(sps_nc0p5))[0]
    retdict["nc_0p5_npcm3"] = nc0p5
    sps_nc1p0 = byte_value[8:16]
    nc1p0 = struct.unpack('<f', bytes.fromhex(sps_nc1p0))[0]
    retdict["nc_1p0_npcm3"] = nc1p0
    sps_nc2p5 = byte_value[16:24]
    nc2p5 = struct.unpack('<f', bytes.fromhex(sps_nc2p5))[0]
    retdict["nc_2p5_npcm3"] = nc2p5
    sps_nc4p0 = byte_value[24:32]
    nc4p0 = struct.unpack('<f', bytes.fromhex(sps_nc4p0))[0]
    retdict["nc_4p0_npcm3"] = nc4p0
    sps_nc10p0 = byte_value[32:40]
    nc10p0 = struct.unpack('<f', bytes.fromhex(sps_nc10p0))[0]
    retdict["nc_10p0_npcm3"] = nc10p0
    sps_mc1p0 = byte_value[40:48]
    mc1p0 = struct.unpack('<f', bytes.fromhex(sps_mc1p0))[0]
    retdict["Mc_1p0_ugpm3"] = mc1p0
    sps_mc2p5 = byte_value[48:56]
    mc2p5 = struct.unpack('<f', bytes.fromhex(sps_mc2p5))[0]
    retdict["Mc_2p5_ugpm3"] = mc2p5
    sps_mc4p0 = byte_value[56:64]
    mc4p0 = struct.unpack('<f', bytes.fromhex(sps_mc4p0))[0]
    retdict["Mc_4p0_ugpm3"] = mc4p0
    sps_mc10p0 = byte_value[64:72]
    mc10p0 = struct.unpack('<f', bytes.fromhex(sps_mc10p0))[0]
    retdict["Mc_10p0_ugpm3"] = mc10p0
    return retdict

def unpack_big(value):
    all_dict = {}
    byte_value = value
    all_dict.update(unpack_bme(byte_value[0:24]))
    all_dict.update(unpack_mic(byte_value[24:48]))
    all_dict.update(unpack_mics(byte_value[48:72]))
    all_dict.update(unpack_sps(byte_value[124:204]))
    all_dict.update(unpack_speco3(byte_value[204:220]))
    return all_dict

def mega_decode_values(item, ret_val, verbose=False):
    retdict = {}
    byte_value = bytes(len(ret_val))
    byte_value = ret_val
    if item == "ALL_IN_ONE":
        retdict = unpack_big(byte_value)
    if verbose:
        print(retdict)
    return retdict

address = "D5902530-C521-271B-C480-EA62930CE7A7"
MODEL_NBR_UUID = "3f4d1809-188d-46bd-869b-e87f342aa36e"
mega_chars_all_in_one = {
    "ALL_IN_ONE": "3f4d1809-188d-46bd-869b-e87f342aa36e"
}

# Main function to read data from the BLE sensor
async def main(address, passphrase):
    data_list = []
    start_time = datetime.now()

    async with BleakClient(address) as client:
        while True:
            ret_val = await client.read_gatt_char(MODEL_NBR_UUID)
            val = binascii.b2a_hex(ret_val).decode()

            for item in mega_chars_all_in_one:
                ret_dict = mega_decode_values(item, val, False)
                after = datetime.now()
                line = {"time": after.strftime('%Y-%m-%dT%H:%M:%S')}
                line.update({key: ret_dict.get(key, None) for key in columns_to_save if key in ret_dict})
                data_list.append(line)
                print(line)

            # Save data and upload CSV every hour
            if datetime.now() - start_time >= timedelta(hours=1):
                csv_file = save_to_csv(data_list)
                handler.upload_file(csv_file)
                data_list.clear()
                start_time = datetime.now()

            time.sleep(5)

if __name__ == "__main__":
    passphrase = getpass.getpass("Enter passphrase for private key: ")
    
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    handler = DataHandler(client, passphrase)

    asyncio.run(main(address, passphrase))
