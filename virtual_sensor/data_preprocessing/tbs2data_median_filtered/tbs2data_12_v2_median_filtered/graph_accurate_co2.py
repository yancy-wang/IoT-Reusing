import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from urllib.parse import unquote

# Define the directory containing CSV files
csv_directory = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_12_v2_filtered"
output_pdf = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_12_v2_filtered/v2_filtered.pdf"

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
'00:0B:57:64:8C:41': '#1f77b4',  # Blue
    '00:0D:6F:20:D4:68': '#ff7f0e',  # Orange
    '90:FD:9F:7B:81:06': '#d62728',  # Red
    '90:FD:9F:7B:83:D6': '#8c564b',  # Brown
    '90:FD:9F:7B:84:EA': '#e377c2',  # Pink
    '90:FD:9F:7B:84:FD': '#bcbd22',  # Yellow-green
    '90:FD:9F:7B:85:2B': '#17becf'   # Cyan
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
            
            # Multiply CO2 data by 100
            if sensor_type == 'CO2(ppm)':
                y_data = y_data * 100
            
            plt.plot(x_data, y_data, label=device_mac, color=color_map.get(device_mac, 'black'))
        plt.xlabel("Time")
        plt.ylabel(sensor_type if sensor_type.lower() != 'co2' else f"{sensor_type} (x100)")
        plt.title(f"{sensor_type} Data Comparison")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

print(f"All plots saved to {output_pdf}.")
