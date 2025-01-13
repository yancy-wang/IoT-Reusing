import pandas as pd

# 读取数据
file_path = '/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_rpi/transmission_times.csv'  # 请更新为您的文件路径
data = pd.read_csv(file_path)

# 将传输时间从秒转换为毫秒
data['Bluetooth Transmission Time (ms)'] = data['Bluetooth Transmission Time (seconds)'] * 1000
data['HTTP Transmission Time (ms)'] = data['HTTP Transmission Time (seconds)'] * 1000

# 定义稳定性计算函数
def calculate_stability(latency_column, error_rate=0):
    mean_latency = latency_column.mean()
    lower_bound = mean_latency * 0.9
    upper_bound = mean_latency * 1.1

    # 计算 K 值：延迟超出平均值 ±10% 的数据比例
    outliers = latency_column[(latency_column < lower_bound) | (latency_column > upper_bound)]
    K = len(outliers) / len(latency_column)

    # 计算稳定性 Ω
    stability = ((1 - error_rate) * (1 - K)) ** 2
    return stability

# 计算稳定性，E 为 0 和 E 为 0.00092 的情况
ble_stability_E0 = calculate_stability(data['Bluetooth Transmission Time (ms)'], error_rate=0)
ble_stability_E_0092 = calculate_stability(data['Bluetooth Transmission Time (ms)'], error_rate=0.00092)
wifi_stability_E0 = calculate_stability(data['HTTP Transmission Time (ms)'], error_rate=0)
wifi_stability_E_0092 = calculate_stability(data['HTTP Transmission Time (ms)'], error_rate=0.00092)

# 输出结果
print(f"BLE Stability (E = 0): {ble_stability_E0:.4f}")
print(f"BLE Stability (E = 0.092%): {ble_stability_E_0092:.4f}")
print(f"Wi-Fi Stability (E = 0): {wifi_stability_E0:.4f}")
print(f"Wi-Fi Stability (E = 0.092%): {wifi_stability_E_0092:.4f}")