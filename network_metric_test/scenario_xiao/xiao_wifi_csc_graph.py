import pandas as pd
import matplotlib.pyplot as plt

# 加载数据集
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao/xiao_wifi_csc.csv'
data = pd.read_csv(file_path)

# 计算统计值
network_min = data['Latency (ms)'].min()
network_max = data['Latency (ms)'].max()
network_mean = data['Latency (ms)'].mean()

# 打印统计值
print(f"Wi-Fi Latency - Min: {network_min:.3f}, Max: {network_max:.3f}, Mean: {network_mean:.3f}")

# 绘制图表

plt.plot(data.index, data['Latency (ms)'], label='Wi-Fi Latency', color='green', linewidth=0.5)
plt.axhline(network_mean, color='green', linestyle='--', label=f'Wi-Fi Latency Mean: {network_mean:.3f} ms')

plt.title('Scenario 5 Latency Measurements')
plt.xlabel('Message Seq.')
plt.ylabel('Latency (ms)')
plt.legend()
plt.grid()
plt.show()
