import pandas as pd
import matplotlib.pyplot as plt

# 加载数据集
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_wio/lora_latency.csv'
data = pd.read_csv(file_path)

# 计算统计值
lora_min = data['LoRaWAN Latency (ms)'].min()
lora_max = data['LoRaWAN Latency (ms)'].max()
lora_mean = data['LoRaWAN Latency (ms)'].mean()

network_min = data['Wi-Fi Latency (ms)'].min()
network_max = data['Wi-Fi Latency (ms)'].max()
network_mean = data['Wi-Fi Latency (ms)'].mean()

# 打印统计值
print(f"Bluetooth Latency - Min: {lora_min:.3f}, Max: {lora_max:.3f}, Mean: {lora_mean:.3f}")
print(f"Wi-Fi Latency - Min: {network_min:.3f}, Max: {network_max:.3f}, Mean: {network_mean:.3f}")

# 绘制图表
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['LoRaWAN Latency (ms)'], label='LoRaWAN Latency', color='blue', linewidth=0.5)
plt.axhline(lora_mean, color='blue', linestyle='--', label=f'LoRaWAN Latency Mean: {lora_mean:.3f} ms')

plt.plot(data.index, data['Wi-Fi Latency (ms)'], label='Wi-Fi Latency', color='green', linewidth=0.5)
plt.axhline(network_mean, color='green', linestyle='--', label=f'Wi-Fi Latency Mean: {network_mean:.3f} ms')

plt.title('Scenario 3 Latency Measurements')
plt.xlabel('Message Seq.')
plt.ylabel('Latency (ms)')
plt.legend()
plt.grid()
plt.show()
