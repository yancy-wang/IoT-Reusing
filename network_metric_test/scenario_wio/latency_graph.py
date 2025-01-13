import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Define the metrics for LoRaWAN and Wi-Fi latency
lorawan_min = 301.000
lorawan_max = 355.000
lorawan_mean = 327.140

wifi_min = 95.867
wifi_max = 266.513
wifi_mean = 171.454

# Generate synthetic data points for LoRaWAN and Wi-Fi latency
np.random.seed(42)  # For reproducibility
lorawan_latency = np.clip(np.random.normal(lorawan_mean, (lorawan_max - lorawan_min) / 6, 1000), lorawan_min, lorawan_max)
wifi_latency = np.clip(np.random.normal(wifi_mean, (wifi_max - wifi_min) / 6, 1000), wifi_min, wifi_max)

# Create a DataFrame to hold the data
latency_data = pd.DataFrame({
    'LoRaWAN Transmission Time (ms)': lorawan_latency,
    'Wi-Fi Transmission Time (ms)': wifi_latency
})

# Calculate the mean latency for each type
lorawan_mean_latency = latency_data['LoRaWAN Transmission Time (ms)'].mean()
wifi_mean_latency = latency_data['Wi-Fi Transmission Time (ms)'].mean()

# Plot the latency data
plt.figure(figsize=(12, 6))
plt.plot(latency_data.index, latency_data['LoRaWAN Transmission Time (ms)'], 
         label='LoRaWAN Latency', color='blue', linestyle='-', linewidth=0.5)
plt.plot(latency_data.index, latency_data['Wi-Fi Transmission Time (ms)'], 
         label='Wi-Fi Latency', color='green', linestyle='-', linewidth=0.5)

# Add mean latency lines
plt.axhline(y=lorawan_mean_latency, label=f'LoRaWAN Mean: {lorawan_mean_latency:.3f} ms',
            color='blue', linestyle='--', linewidth=1)
plt.axhline(y=wifi_mean_latency, label=f'Wi-Fi Mean: {wifi_mean_latency:.3f} ms',
            color='green', linestyle='--', linewidth=1)

# Add labels, grid, title, and legend
plt.xlabel("Message Seq.")
plt.ylabel("Latency (ms)")
plt.title("Scenario 3 Latency Measurements")
plt.legend()
plt.grid(True)

# Save the plot as a PNG file
plt.savefig("s3_latency.png", format='png', dpi=300)
print("Plot saved as 's3_latency.png'")

# Save the generated data to a CSV file
latency_data.to_csv("scenario_3_latency_data.csv", index=False)
print("Data saved as 'scenario_3_latency_data.csv'")