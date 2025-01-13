import pandas as pd
import matplotlib.pyplot as plt

# 加载数据集
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_iphone/iphone_csc_latency.csv'
data = pd.read_csv(file_path)

# 计算统计值
bluetooth_min = data['Bluetooth Latency (ms)'].min()
bluetooth_max = data['Bluetooth Latency (ms)'].max()
bluetooth_mean = data['Bluetooth Latency (ms)'].mean()

network_min = data['Network Latency (ms)'].min()
network_max = data['Network Latency (ms)'].max()
network_mean = data['Network Latency (ms)'].mean()

# 打印统计值
print(f"Bluetooth Latency - Min: {bluetooth_min:.3f}, Max: {bluetooth_max:.3f}, Mean: {bluetooth_mean:.3f}")
print(f"4G Latency - Min: {network_min:.3f}, Max: {network_max:.3f}, Mean: {network_mean:.3f}")

# 绘制图表
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['Bluetooth Latency (ms)'], label='Bluetooth Latency', color='blue', linewidth=0.5)
plt.axhline(bluetooth_mean, color='blue', linestyle='--', label=f'Bluetooth Latency Mean: {bluetooth_mean:.3f} ms')

plt.plot(data.index, data['Network Latency (ms)'], label='4G Latency', color='green', linewidth=0.5)
plt.axhline(network_mean, color='green', linestyle='--', label=f'4G Latency Mean: {network_mean:.3f} ms')

plt.title('Scenario 1 Latency Measurements')
plt.xlabel('Message Seq.')
plt.ylabel('Latency (ms)')
plt.legend()
plt.grid()
plt.show()
