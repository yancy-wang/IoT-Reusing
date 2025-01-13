import pandas as pd

# Load the CSV file
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_iphone/latency_results_4G.csv'  # 更新为实际路径
data = pd.read_csv(file_path)

# 定义稳定性计算函数
def calculate_stability(latency_column, error_rate=0):
    # 计算平均延迟
    mean_latency = latency_column.mean()
    
    # 计算±10%的平均延迟范围
    lower_bound = mean_latency * 0.9
    upper_bound = mean_latency * 1.1
    
    # 计算 K 值，表示延迟超出 ±10% 的比例
    outliers = latency_column[(latency_column < lower_bound) | (latency_column > upper_bound)]
    K = len(outliers) / len(latency_column)
    
    # 计算稳定性
    stability = ((1 - error_rate) * (1 - K)) ** 2
    return stability

# 计算 BLE 和 4G 的稳定性
ble_stability_E0 = calculate_stability(data['Bluetooth Latency (ms)'], error_rate=0)
ble_stability_E4_147 = calculate_stability(data['Bluetooth Latency (ms)'], error_rate=0.04147)
network_stability_E0 = calculate_stability(data['Network Latency (ms)'], error_rate=0)
network_stability_E4_147 = calculate_stability(data['Network Latency (ms)'], error_rate=0.04147)

# 显示结果
print(f"Bluetooth Stability (E = 0): {ble_stability_E0:.4f}")
print(f"Bluetooth Stability (E = 4.147%): {ble_stability_E4_147:.4f}")
print(f"Network Stability (E = 0): {network_stability_E0:.4f}")
print(f"Network Stability (E = 4.147%): {network_stability_E4_147:.4f}")