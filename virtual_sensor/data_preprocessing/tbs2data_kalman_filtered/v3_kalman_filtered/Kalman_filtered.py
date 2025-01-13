import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from urllib.parse import unquote

class KalmanFilter:
    def __init__(self, process_variance, measurement_variance, estimated_measurement_variance):
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def update(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        return self.posteri_estimate

def apply_kalman_filter(data, process_variance, measurement_variance, estimated_measurement_variance):
    kalman_filter = KalmanFilter(process_variance, measurement_variance, estimated_measurement_variance)
    filtered_data = [kalman_filter.update(measurement) for measurement in data]
    return filtered_data

def process_outliers(series, window_size=5, threshold=3):
    rolling_median = series.rolling(window=window_size, center=True).median()
    rolling_std = series.rolling(window=window_size, center=True).std()
    diff = np.abs(series - rolling_median)
    outliers = diff > (threshold * rolling_std)
    series[outliers] = rolling_median[outliers]
    return series

input_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_without0/tbs2data_12_v3_without0"
output_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v3_kalman_filtered"
output_pdf = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v3_kalman_filtered/Kalman_v3_filtered.pdf"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

csv_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]

sensor_columns = ['Temperature(°C)', 'Ambient light(x)', 'Pressure(mbar)', 'humidity(%)', 'sound level(dB)', 'CO2(ppm)', 'VOCs(ppb)']

process_variance = 1e-5
measurement_variance = 1e-2
estimated_measurement_variance = 1e-2

for csv_file in csv_files:
    df = pd.read_csv(csv_file)
    
    for column in sensor_columns:
        if column in df.columns:
            df[column] = process_outliers(df[column])
            df[column] = apply_kalman_filter(df[column], process_variance, measurement_variance, estimated_measurement_variance)
    
    output_csv = os.path.join(output_folder, os.path.basename(csv_file))
    df.to_csv(output_csv, index=False)

print("All files processed and saved to the output folder.")

# Define the directory containing processed CSV files
csv_directory = output_folder

# Get a list of all CSV files in the directory
csv_files = [os.path.join(csv_directory, f) for f in os.listdir(csv_directory) if f.endswith('.csv')]

# Check if there are any CSV files in the directory
if not csv_files:
    print("No CSV files found in the specified directory.")
    exit()

# Group CSV files by device MAC address
device_data = {}
for csv_file in csv_files:
    file_name = os.path.basename(csv_file)
    encoded_mac = file_name.split('_')[0]
    device_mac = unquote(encoded_mac)
    print(device_mac)
    if device_mac not in device_data:
        device_data[device_mac] = []
    device_data[device_mac].append(csv_file)

# Sort the files for each device to ensure they are in chronological order
for mac in device_data:
    device_data[mac].sort()

# Define the colors for each device MAC address based on the provided image
color_map = {
    '00:0D:6F:20:D3:F3': '#1f77b4',  # Blue
    '00:0D:6F:20:D4:96': '#ff7f0e',  # Orange
    '90:FD:9F:7B:81:06': '#d62728',  # Red
    '90:FD:9F:7B:82:50': '#8c564b',  # Brown
    '90:FD:9F:7B:83:D1': '#e377c2',  # Pink
    '90:FD:9F:7B:83:D6': '#bcbd22',  # Yellow-green
    '90:FD:9F:7B:84:67': '#17becf'   # Cyan
}

# Read the first file to get the sensor types
sample_df = pd.read_csv(csv_files[0])
sensor_types = sample_df.columns[1:]  # Assuming the first column is Timestamp and rest are sensor types

# Remove 'Timestamp' from sensor_types if it exists
sensor_types = [sensor for sensor in sensor_types if sensor.lower() != 'timestamp']

# Create a PDF to save the plots
with PdfPages(output_pdf) as pdf:
    for sensor_type in sensor_types:
        plt.figure(figsize=(10, 6))
        for device_mac, files in device_data.items():
            combined_df = pd.concat([pd.read_csv(f) for f in files])
            combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
            combined_df.sort_values('Timestamp', inplace=True)
            x_data = combined_df["Timestamp"]
            y_data = combined_df[sensor_type]
            
            plt.plot(x_data, y_data, label=device_mac, color=color_map.get(device_mac, 'black'))
        plt.xlabel("Time")
        plt.ylabel(sensor_type)
        plt.title(f"{sensor_type} Data Comparison")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

print(f"All plots saved to {output_pdf}.")
