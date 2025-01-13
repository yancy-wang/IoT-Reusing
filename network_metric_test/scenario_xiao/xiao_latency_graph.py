import pandas as pd
import matplotlib.pyplot as plt

# 加载 CSV 文件
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao/wifi_latencylatency_data.csv'  # 替换为您的文件路径
data = pd.read_csv(file_path)

# 计算最大、最小和平均延时
max_latency = data['Latency (ms)'].max()
min_latency = data['Latency (ms)'].min()
avg_latency = data['Latency (ms)'].mean()

# 绘制延时图
plt.figure(figsize=(12, 6))
plt.plot(data['Latency (ms)'], color='blue', linewidth=0.5)
plt.axhline(avg_latency, color='blue', linestyle='--', label=f'Wi-Fi Mean Latency: {avg_latency:.2f} ms')
plt.title('Scenario 5 Latency Measurements')
plt.xlabel('Message Seq.')
plt.ylabel('Latency (ms)')
plt.legend()
plt.grid()

# 保存图像
output_image_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_xiao/s5_latency.png'  # 替换为您想保存的路径
plt.savefig(output_image_path, format='png', dpi=300)
plt.show()

# 打印最大、最小和平均延时
print(f"Maximum Latency: {max_latency} ms")
print(f"Minimum Latency: {min_latency} ms")
print(f"Average Latency: {avg_latency:.2f} ms")