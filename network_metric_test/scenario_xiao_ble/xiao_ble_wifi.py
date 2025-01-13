import pandas as pd
import matplotlib.pyplot as plt

# Load the data from the files
bluetooth_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/bluetooth_transmission_times.csv'
wifi_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/wifi_latency_data.csv'

# Load Bluetooth and Wi-Fi latency data
bluetooth_data = pd.read_csv(bluetooth_file_path)
wifi_data = pd.read_csv(wifi_file_path)

# Rename columns to standardize for plotting
bluetooth_data.columns = ['Bluetooth Transmission Time (ms)']
wifi_data = wifi_data.rename(columns={'Latency (ms)': 'Wi-Fi Transmission Time (ms)'})

# Merge the data based on the index
latency_data = pd.concat([bluetooth_data, wifi_data['Wi-Fi Transmission Time (ms)']], axis=1)

# Calculate min, max, and mean latency for each type
bluetooth_min_latency = round(latency_data['Bluetooth Transmission Time (ms)'].min(), 3)
bluetooth_max_latency = round(latency_data['Bluetooth Transmission Time (ms)'].max(), 3)
bluetooth_mean_latency = round(latency_data['Bluetooth Transmission Time (ms)'].mean(), 3)

wifi_min_latency = round(latency_data['Wi-Fi Transmission Time (ms)'].min(), 3)
wifi_max_latency = round(latency_data['Wi-Fi Transmission Time (ms)'].max(), 3)
wifi_mean_latency = round(latency_data['Wi-Fi Transmission Time (ms)'].mean(), 3)

# Print minimum, maximum, and mean latency
print(f"Bluetooth Min Latency: {bluetooth_min_latency} ms")
print(f"Bluetooth Max Latency: {bluetooth_max_latency} ms")
print(f"Bluetooth Mean Latency: {bluetooth_mean_latency} ms")

print(f"Wi-Fi Min Latency: {wifi_min_latency} ms")
print(f"Wi-Fi Max Latency: {wifi_max_latency} ms")
print(f"Wi-Fi Mean Latency: {wifi_mean_latency} ms")

# Plot the latency data
plt.figure(figsize=(12, 6))
plt.plot(latency_data.index, latency_data['Bluetooth Transmission Time (ms)'], 
         label='Bluetooth Latency (ms)', color='blue', linestyle='-', linewidth=0.5)
plt.plot(latency_data.index, latency_data['Wi-Fi Transmission Time (ms)'], 
         label='Wi-Fi Latency (ms)', color='green', linestyle='-', linewidth=0.5)

# Add mean latency lines
plt.axhline(y=bluetooth_mean_latency, color='blue', linestyle='--', linewidth=1,
            label=f'Bluetooth Mean: {bluetooth_mean_latency} ms')
plt.axhline(y=wifi_mean_latency, color='green', linestyle='--', linewidth=1,
            label=f'Wi-Fi Mean: {wifi_mean_latency} ms')

# Add labels, grid, title, and legend
plt.xlabel("Message Seq.")
plt.ylabel("Latency (ms)")
plt.title("Scenario 4 Latency Measurements")
plt.legend(loc='upper right')
plt.grid(True)

# Save the plot as a PNG file
output_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/s3_latency.png'
plt.savefig(output_path, format='png', dpi=300)
print(f"Plot saved to {output_path}")

# Show plot
plt.show()