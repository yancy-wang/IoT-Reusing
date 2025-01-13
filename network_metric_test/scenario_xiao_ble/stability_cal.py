import pandas as pd

# Load the data from the files
bluetooth_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/bluetooth_transmission_times.csv'
wifi_file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao_ble/wifi_latencylatency_data.csv'

# Load Bluetooth and Wi-Fi latency data
bluetooth_data = pd.read_csv(bluetooth_file_path)
wifi_data = pd.read_csv(wifi_file_path)

# Define function to calculate stability
def calculate_stability(latency_data, error_rate=0):
    mean_latency = latency_data.mean()
    lower_bound = mean_latency * 0.9
    upper_bound = mean_latency * 1.1
    
    # Calculate K, the proportion of values outside ±10% of the mean latency
    outliers = latency_data[(latency_data < lower_bound) | (latency_data > upper_bound)]
    K = len(outliers) / len(latency_data)
    
    # Calculate stability with the given error rate
    stability = ((1 - error_rate) * (1 - K)) ** 2
    return stability

# Calculate stability for Bluetooth and Wi-Fi with E = 0% and E = 4.602%
bluetooth_stability_E0 = calculate_stability(bluetooth_data['Bluetooth Transmission Time (ms)'], error_rate=0)
bluetooth_stability_E04602 = calculate_stability(bluetooth_data['Bluetooth Transmission Time (ms)'], error_rate=0.04602)

wifi_stability_E0 = calculate_stability(wifi_data['Latency (ms)'], error_rate=0)
wifi_stability_E04602 = calculate_stability(wifi_data['Latency (ms)'], error_rate=0.04602)

# Display results
print(f"Bluetooth Stability (E = 0%): {bluetooth_stability_E0:.4f}")
print(f"Bluetooth Stability (E = 4.602%): {bluetooth_stability_E04602:.4f}")
print(f"Wi-Fi Stability (E = 0%): {wifi_stability_E0:.4f}")
print(f"Wi-Fi Stability (E = 4.602%): {wifi_stability_E04602:.4f}")