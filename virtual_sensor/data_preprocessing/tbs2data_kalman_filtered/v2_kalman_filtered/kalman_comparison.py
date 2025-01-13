import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from urllib.parse import unquote
from scipy.spatial.distance import euclidean

# Define the directory containing original and adjusted CSV files
original_csv_directory = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_12/tbs2data_12_v2"
input_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_without0/tbs2data_12_v2_without0"
output_pdf = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_original_adjust/tbs2data_12_v2/sensor_data_comparison_combined.pdf"
adjusted_csv_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_adjusted_csv/v2"
intercept_file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_original_adjust/tbs2data_12_v2/adjustments.csv"

# MAC address to sensor number mapping
mac_to_sensor = {
    '90:FD:9F:7B:85:2B': 'Sensor 1',
    '90:FD:9F:7B:84:FD': 'Sensor 2',
    '90:FD:9F:7B:83:D6': 'Sensor 3',
    '90:FD:9F:7B:81:06': 'Sensor 4',
    '90:FD:9F:7B:84:EA': 'Sensor 5',
    '00:0D:6F:20:D4:68': 'Sensor 7',
    '00:0B:57:64:8C:41': 'Sensor 8'
}

# Define color mapping for sensors
color_map = {
    'Sensor 1': '#1f77b4',  # Blue
    'Sensor 2': '#ff7f0e',  # Orange
    'Sensor 3': '#d62728',  # Red
    'Sensor 4': '#8c564b',  # Brown
    'Sensor 5': '#e377c2',  # Pink
    'Sensor 7': '#bcbd22',  # Yellow-green
    'Sensor 8': '#17becf'   # Cyan
}

# Function to replace MAC address with sensor number in DataFrame columns
def replace_mac_with_sensor(df, mac_to_sensor):
    df.columns = [mac_to_sensor.get(col, col) for col in df.columns]
    return df

# Function to calculate consistency
def calculate_consistency(data1, data2):
    valid_indices = ~np.isnan(data1) & ~np.isnan(data2)
    data1 = data1[valid_indices]
    data2 = data2[valid_indices]
    correlation = np.corrcoef(data1, data2)[0, 1] if len(data1) > 0 and len(data2) > 0 else np.nan
    mae = np.mean(np.abs(data1 - data2)) if len(data1) > 0 and len(data2) > 0 else np.nan
    return correlation, mae

# Function to find reference MAC address
def find_reference_mac(df, mac_list):
    df_filled = df.fillna(df.mean())
    mean_values = df_filled.mean(axis=1)
    distances = {mac: euclidean(mean_values, df_filled[mac]) for mac in mac_list}
    return min(distances, key=distances.get)

# Function to adjust data
def adjust_data(df, reference_mac):
    adjustments = {mac: df[reference_mac].mean() - df[mac].mean() for mac in df.columns if mac != reference_mac}
    for mac, adjustment in adjustments.items():
        df[mac] += adjustment
    return df, adjustments

# Function to generate original plots
def generate_original_plots():
    original_csv_files = [os.path.join(original_csv_directory, f) for f in os.listdir(original_csv_directory) if f.endswith('.csv')]

    if not original_csv_files:
        print("No CSV files found in the specified directory.")
        return None, None

    original_device_data = {}
    for csv_file in original_csv_files:
        file_name = os.path.basename(csv_file)
        encoded_mac = file_name.split('_')[0]
        device_mac = unquote(encoded_mac)
        if device_mac not in original_device_data:
            original_device_data[device_mac] = []
        original_device_data[device_mac].append(csv_file)

    for mac in original_device_data:
        original_device_data[mac].sort()

    sample_df = pd.read_csv(original_csv_files[0])
    sensor_types = sample_df.columns[1:]

    sensor_types = [sensor for sensor in sensor_types if sensor.lower() != 'timestamp']

    return original_device_data, sensor_types

# Function to generate adjusted plots and save adjusted CSV files
def generate_adjusted_plots():
    csv_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]

    if not csv_files:
        print("No CSV files found in the specified directory.")
        return None, None

    device_data = {}
    for csv_file in csv_files:
        file_name = os.path.basename(csv_file)
        encoded_mac = file_name.split('_')[0]
        device_mac = unquote(encoded_mac)
        if device_mac not in device_data:
            device_data[device_mac] = []
        device_data[device_mac].append(csv_file)

    for mac in device_data:
        device_data[mac].sort()

    sample_df = pd.read_csv(csv_files[0])
    sensor_types = sample_df.columns[1:]

    sensor_types = [sensor for sensor in sensor_types if sensor.lower() != 'timestamp']

    combined_data = {}
    for mac, files in device_data.items():
        df_list = [pd.read_csv(f) for f in files]
        combined_df = pd.concat(df_list).sort_values('Timestamp').reset_index(drop=True)
        combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
        combined_df['Index'] = combined_df.index
        combined_data[mac] = combined_df

    adjustments_records = []
    for sensor_type in sensor_types:
        mac_list = list(combined_data.keys())
        consistency_results = []
        for i in range(len(mac_list)):
            for j in range(i + 1, len(mac_list)):
                mac1 = mac_list[i]
                mac2 = mac_list[j]
                data1 = combined_data[mac1][sensor_type].dropna().values
                data2 = combined_data[mac2][sensor_type].dropna().values
                min_length = min(len(data1), len(data2))
                data1_aligned = data1[:min_length]
                data2_aligned = data2[:min_length]
                if len(data1_aligned) > 0 and len(data2_aligned) > 0:
                    correlation, mae = calculate_consistency(data1_aligned, data2_aligned)
                    if correlation > 0.95:
                        consistency_results.append((mac1, mac2, correlation, mae))

        high_correlation_macs = set()
        for result in consistency_results:
            mac1, mac2, correlation, mae = result
            high_correlation_macs.add(mac1)
            high_correlation_macs.add(mac2)

        if not high_correlation_macs:
            continue

        high_corr_df = pd.DataFrame({mac: combined_data[mac][sensor_type] for mac in high_correlation_macs})
        high_corr_df['Timestamp'] = combined_data[next(iter(high_correlation_macs))]['Timestamp']
        reference_mac = find_reference_mac(high_corr_df.drop(columns=['Timestamp']), high_correlation_macs)
        adjusted_df, adjustments = adjust_data(high_corr_df.drop(columns=['Timestamp']).copy(), reference_mac)
        adjusted_df['Timestamp'] = high_corr_df['Timestamp']
        for mac, adjustment in adjustments.items():
            adjustments_records.append({
                'Sensor': sensor_type,
                'MAC': mac,
                'Reference MAC': reference_mac,
                'Adjustment': adjustment
            })

        adjusted_df = replace_mac_with_sensor(adjusted_df, mac_to_sensor)
        for mac in high_correlation_macs:
            sensor_number = mac_to_sensor.get(mac, mac)
            adjusted_file_path = os.path.join(adjusted_csv_folder, f'{sensor_number}_{sensor_type}_adjusted.csv')
            adjusted_df[['Timestamp', sensor_number]].to_csv(adjusted_file_path, index=False)

    adjustments_df = pd.DataFrame(adjustments_records)
    adjustments_df.to_csv(intercept_file_path, index=False)
    return device_data, sensor_types

# Plot original and adjusted data together
def plot_comparison(original_device_data, adjusted_device_data, sensor_types):
    with PdfPages(output_pdf) as pdf:
        for sensor_type in sensor_types:
            fig, axs = plt.subplots(2, 1, figsize=(10, 12))

            # Plot original data
            for device_mac, files in original_device_data.items():
                combined_df = pd.concat([pd.read_csv(f) for f in files])
                combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
                combined_df.sort_values('Timestamp', inplace=True)
                x_data = combined_df["Timestamp"]
                y_data = combined_df[sensor_type]

                if sensor_type == 'CO2(ppm)':
                    y_data = y_data * 100

                axs[0].plot(x_data, y_data, label=f'{mac_to_sensor.get(device_mac, device_mac)} (Original)', color=color_map.get(mac_to_sensor.get(device_mac, device_mac), 'black'))

            axs[0].set_xlabel("Time")
            axs[0].set_ylabel(sensor_type if sensor_type.lower() != 'co2' else f"{sensor_type} (x100)")
            axs[0].set_title(f"Original {sensor_type} Data")
            axs[0].legend()
            axs[0].tick_params(axis='x', rotation=45)

            # Plot adjusted data
            for device_mac, files in adjusted_device_data.items():
                combined_df = pd.concat([pd.read_csv(f) for f in files])
                combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
                combined_df.sort_values('Timestamp', inplace=True)
                x_data = combined_df["Timestamp"]
                y_data = combined_df[sensor_type]

                if sensor_type == 'CO2(ppm)':
                    y_data = y_data * 100

                axs[1].plot(x_data, y_data, label=f'{mac_to_sensor.get(device_mac, device_mac)} (Adjusted)', color=color_map.get(mac_to_sensor.get(device_mac, device_mac), 'black'))

            axs[1].set_xlabel("Time")
            axs[1].set_ylabel(sensor_type if sensor_type.lower() != 'co2' else f"{sensor_type} (x100)")
            axs[1].set_title(f"Adjusted {sensor_type} Data")
            axs[1].legend()
            axs[1].tick_params(axis='x', rotation=45)

            plt.tight_layout()
            pdf.savefig(fig)
            plt.close()

    print(f"All plots saved to {output_pdf}.")

# Main function to execute the plotting
def main():
    original_device_data, sensor_types = generate_original_plots()
    adjusted_device_data, _ = generate_adjusted_plots()
    plot_comparison(original_device_data, adjusted_device_data, sensor_types)

if __name__ == "__main__":
    main()
