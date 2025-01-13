import requests
from requests.auth import HTTPBasicAuth
import time
import csv
from datetime import datetime

# configuration
API_ID = '7GP3FE1OXWXITCBX'
API_KEY = 'C73D301BC3BA4FDAB812C3D2025647C5228DAB366FA24C13A9ADE182BD837BF4'
DEVICE_EUI = '2CF7F1F054800005'
URL = 'https://sensecap.seeed.cc/openapi/list_telemetry_data'

# Timestamp
time_end = int(time.time() * 1000)
time_start = time_end - 3600 * 1000

# params
temperature_params = {
    'device_eui': DEVICE_EUI,
    'measurement_id': '4097',
    'limit': 100,
    'time_start': time_start,
    'time_end': time_end
}

humidity_params = {
    'device_eui': DEVICE_EUI,
    'measurement_id': '4098',
    'limit': 100,
    'time_start': time_start,
    'time_end': time_end
}

vocs_params = {
    'device_eui': DEVICE_EUI,
    'measurement_id': '4206',
    'limit': 100,
    'time_start': time_start,
    'time_end': time_end
}

noise_params = {
    'device_eui': DEVICE_EUI,
    'measurement_id': '4207',
    'limit': 100,
    'time_start': time_start,
    'time_end': time_end
}

response_temperature = requests.get(URL, auth=HTTPBasicAuth(API_ID, API_KEY), params=temperature_params)
response_humidity = requests.get(URL, auth=HTTPBasicAuth(API_ID, API_KEY), params=humidity_params)
response_vocs = requests.get(URL, auth=HTTPBasicAuth(API_ID, API_KEY), params=vocs_params)
response_noise = requests.get(URL, auth=HTTPBasicAuth(API_ID, API_KEY), params=noise_params)

temperature_data = []
if response_temperature.status_code == 200:
    data = response_temperature.json()
    measurements = data['data']['list'][1][0]
    for measurement in measurements:
        timestamp = measurement[1]
        value = measurement[0]
        temperature_data.append((timestamp, value))
else:
    print(f"Error temperature status code: {response_temperature.status_code}")

humidity_data = []
if response_humidity.status_code == 200:
    data = response_humidity.json()
    measurements = data['data']['list'][1][0]
    for measurement in measurements:
        timestamp = measurement[1]
        value = measurement[0]
        humidity_data.append((timestamp, value))
else:
    print(f"Error humidity status code: {response_humidity.status_code}")

vocs_data = []
if response_vocs.status_code == 200:
    data = response_vocs.json()
    measurements = data['data']['list'][1][0]
    for measurement in measurements:
        timestamp = measurement[1]
        value = measurement[0]
        vocs_data.append((timestamp, value))
else:
    print(f"Error VOCs index status code: {response_vocs.status_code}")

noise_data = []
if response_noise.status_code == 200:
    data = response_noise.json()
    measurements = data['data']['list'][1][0]
    for measurement in measurements:
        timestamp = measurement[1]
        value = measurement[0]
        noise_data.append((timestamp, value))
else:
    print(f"Error noise status code: {response_noise.status_code}")


# save temperature, humidity, VOCs index, and noise into csv file
with open('/Users/wangyangyang/Desktop/Finland/summer_job/LoRaWAN/sensor_data.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Timestamp', 'Temperature (C)', 'Humidity (%)', 'VOCS Index', 'Noise (dB)'])

    # Merge the data
    combined_data = {}
    for timestamp, value in temperature_data:
        if timestamp not in combined_data:
            combined_data[timestamp] = {}
        combined_data[timestamp]['Temperature (C)'] = value

    for timestamp, value in humidity_data:
        if timestamp not in combined_data:
            combined_data[timestamp] = {}
        combined_data[timestamp]['Humidity (%)'] = value

    for timestamp, value in vocs_data:
        if timestamp not in combined_data:
            combined_data[timestamp] = {}
        combined_data[timestamp]['VOCS Index'] = value

    for timestamp, value in noise_data:
        if timestamp not in combined_data:
            combined_data[timestamp] = {}
        combined_data[timestamp]['Noise (dB)'] = value

    # written into csv file
    for timestamp in sorted(combined_data.keys()):
        temperature = combined_data[timestamp].get('Temperature (C)', '')
        humidity = combined_data[timestamp].get('Humidity (%)', '')
        vocs_index = combined_data[timestamp].get('VOCS Index', '')
        noise = combined_data[timestamp].get('Noise (dB)', '')
        writer.writerow([timestamp, temperature, humidity, vocs_index, noise])

print(f"The data has been saved into sensor_data.csv")
