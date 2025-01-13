import pandas as pd
import matplotlib.pyplot as plt

# Load the data from CSV
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_rpi/transmission_times.csv'  # Replace with your actual file path
data = pd.read_csv(file_path)

# Extract Bluetooth and 4G transmission time columns and convert to milliseconds
bluetooth_latency = data['Bluetooth Transmission Time (seconds)'] * 1000  # Convert to ms
network_latency = data['HTTP Transmission Time (seconds)'] * 1000  # Convert to ms, renamed to 4G

# Calculate max, min, and mean latency for Bluetooth and 4G
max_bluetooth_latency = bluetooth_latency.max()
min_bluetooth_latency = bluetooth_latency.min()
mean_bluetooth_latency = bluetooth_latency.mean()

max_network_latency = network_latency.max()
min_network_latency = network_latency.min()
mean_network_latency = network_latency.mean()

# Print latency summary
print(f"Bluetooth Transmission Time (ms) - Max: {max_bluetooth_latency:.3f}, Min: {min_bluetooth_latency:.3f}, Mean: {mean_bluetooth_latency:.3f}")
print(f"Wi-Fi Transmission Time (ms) - Max: {max_network_latency:.3f}, Min: {min_network_latency:.3f}, Mean: {mean_network_latency:.3f}")

# Plot Bluetooth and 4G latency only
plt.figure(figsize=(12, 6))

plt.plot(bluetooth_latency, label='Bluetooth Latency', color='blue', linewidth=0.5)
plt.axhline(mean_bluetooth_latency, color='blue', linestyle='--', label=f'Bluetooth Mean: {mean_bluetooth_latency:.2f} ms')

plt.plot(network_latency, label='Wi-Fi Latency', color='green', linewidth=0.5)
plt.axhline(mean_network_latency, color='green', linestyle='--', label=f'Wi-Fi Mean: {mean_network_latency:.2f} ms')

# Add titles, labels, and legend
plt.title('Scenario 2 Latency Measurements')
plt.xlabel('Message Seq.')
plt.ylabel('Latency (ms)')
plt.legend()
plt.grid()

# Save the plot as a PNG file
output_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_rpi/s2_latency.png'  # Replace with your desired save location
plt.savefig(output_path, format='png', dpi=300)

# Display the plot
plt.show()