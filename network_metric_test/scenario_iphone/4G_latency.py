import pandas as pd
import matplotlib.pyplot as plt

# Load the data
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_iphone/latency_results_4G.csv'  # Replace with your actual file path
data = pd.read_csv(file_path)

# Extract Bluetooth and Network (4G) latency columns
bluetooth_latency = data['Bluetooth Latency (ms)']
network_latency = data['Network Latency (ms)']

# Calculate max, min, and mean latency for Bluetooth and 4G
max_bluetooth_latency = bluetooth_latency.max()
min_bluetooth_latency = bluetooth_latency.min()
mean_bluetooth_latency = bluetooth_latency.mean()

max_network_latency = network_latency.max()
min_network_latency = network_latency.min()
mean_network_latency = network_latency.mean()

# Print latency summary
print(f"Bluetooth Latency (ms) - Max: {max_bluetooth_latency}, Min: {min_bluetooth_latency}, Mean: {mean_bluetooth_latency}")
print(f"4G Network Latency (ms) - Max: {max_network_latency}, Min: {min_network_latency}, Mean: {mean_network_latency}")

# Plot Bluetooth and 4G latency
plt.figure(figsize=(12, 6))
plt.plot(bluetooth_latency, label='Bluetooth Latency', color='blue', linewidth=0.5)
plt.axhline(mean_bluetooth_latency, color='blue', linestyle='--', label=f'Bluetooth Mean: {mean_bluetooth_latency:.2f} ms')

plt.plot(network_latency, label='Network Latency (4G)', color='green', linewidth=0.5)
plt.axhline(mean_network_latency, color='green', linestyle='--', label=f'Network (4G) Mean: {mean_network_latency:.2f} ms')

# Add titles and labels
plt.title('Bluetooth and 4G Network Latency Measurements')
plt.xlabel('Message Seq.')
plt.ylabel('Latency (ms)')
plt.legend()
plt.grid()

# Display the plot
plt.show()