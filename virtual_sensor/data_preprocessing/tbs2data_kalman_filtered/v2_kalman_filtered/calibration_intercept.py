import os
import pandas as pd
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from urllib.parse import unquote
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean

def calculate_consistency(data1, data2):
    valid_indices = ~np.isnan(data1) & ~np.isnan(data2)
    data1 = data1[valid_indices]
    data2 = data2[valid_indices]
    correlation = np.corrcoef(data1, data2)[0, 1] if len(data1) > 0 and len(data2) > 0 else np.nan
    mse = np.mean((data1 - data2) ** 2) if len(data1) > 0 and len(data2) > 0 else np.nan
    return correlation, mse

def find_reference_sensor(df, sensor_list):
    df_filled = df.fillna(df.mean())
    mean_values = df_filled.mean(axis=1)
    distances = {sensor: euclidean(mean_values, df_filled[sensor]) for sensor in sensor_list}
    return min(distances, key=distances.get)

def adjust_data(df, reference_sensor):
    adjustments = {sensor: df[reference_sensor].mean() - df[sensor].mean() for sensor in df.columns if sensor != reference_sensor}
    for sensor, adjustment in adjustments.items():
        df[sensor] += adjustment
    return df

def plot_adjusted_data(sensor_type, combined_data, adjusted_data, output_folder):
    for sensor in adjusted_data.columns:
        if sensor == 'Timestamp':
            continue
        plt.figure(figsize=(10, 6))
        plt.plot(combined_data[sensor]['Timestamp'], combined_data[sensor][sensor_type], label=f'Original {sensor}')
        plt.plot(adjusted_data['Timestamp'], adjusted_data[sensor], label=f'Adjusted {sensor}')
        plt.xlabel('Timestamp')
        plt.ylabel(sensor_type)
        plt.title(f'Adjusted {sensor_type} Data for {sensor}')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(output_folder, f'{sensor_type}_adjusted_{sensor}.png'))
        plt.close()

# 定义映射表
mac_to_sensor = {
    '90:FD:9F:7B:85:2B': 'Sensor 1',
    '90:FD:9F:7B:84:FD': 'Sensor 2',
    '90:FD:9F:7B:83:D6': 'Sensor 3',
    '90:FD:9F:7B:81:06': 'Sensor 4',
    '90:FD:9F:7B:84:EA': 'Sensor 5',
    '00:0D:6F:20:D4:68': 'Sensor 7',
    '00:0B:57:64:8C:41': 'Sensor 8'
}

# 定义颜色映射表
color_map = {
    'Sensor 1': '#1f77b4',  # Blue
    'Sensor 2': '#ff7f0e',  # Orange
    'Sensor 3': '#d62728',  # Red
    'Sensor 4': '#8c564b',  # Brown
    'Sensor 5': '#e377c2',  # Pink
    'Sensor 7': '#bcbd22',  # Yellow-green
    'Sensor 8': '#17becf'   # Cyan
}

sensor_rename_map = {
    'Temperature(°C)': 'Temperature (°C)',
    'Ambient light(x)': 'Ambient Light (lux)',
    'humidity(%)': 'Humidity (%)',
    'sound level(dB)': 'Sound Level (dB)',
    'CO2(ppm)': 'CO2 (ppm)',
    'VOCs(ppb)': 'VOCs (ppb)',
    'Pressure(mbar)': 'Pressure (mbar)'
}

# 定义输入和输出目录
input_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_kalman_filtered"
output_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_calibration_intercept/plots"
adjusted_csv_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_calibration_intercept"

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)
os.makedirs(adjusted_csv_folder, exist_ok=True)

# 获取所有处理过的CSV文件
csv_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith('.csv')]

if not csv_files:
    print("No CSV files found in the specified directory.")
    exit()

# 按设备MAC地址分组CSV文件
device_data = {}
for csv_file in csv_files:
    file_name = os.path.basename(csv_file)
    encoded_mac = file_name.split('_')[0]
    device_mac = unquote(encoded_mac)
    sensor = mac_to_sensor.get(device_mac, device_mac)  # 使用传感器名称而非MAC地址
    if sensor not in device_data:
        device_data[sensor] = []
    device_data[sensor].append(csv_file)

# 确保每个设备的文件按时间顺序排序
for sensor in device_data:
    device_data[sensor].sort()

# 读取第一个文件以获取传感器类型
sample_df = pd.read_csv(csv_files[0])
sensor_types = sample_df.columns[1:]  # 假设第一列是时间戳，剩下的是传感器类型

# 去掉'Timestamp'列
sensor_types = [sensor for sensor in sensor_types if sensor.lower() != 'timestamp']

# 合并每个设备的CSV文件，并给每个时间点按顺序编号
combined_data = {}
for sensor, files in device_data.items():
    df_list = [pd.read_csv(f) for f in files]
    combined_df = pd.concat(df_list).sort_values('Timestamp').reset_index(drop=True)
    combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
    combined_df['Index'] = combined_df.index
    combined_data[sensor] = combined_df

# 处理每个传感器项
for sensor_type in sensor_types:
    mac_list = list(combined_data.keys())
    consistency_results = []
    
    # 计算每对设备之间的相似度
    for i in range(len(mac_list)):
        for j in range(i + 1, len(mac_list)):
            sensor1 = mac_list[i]
            sensor2 = mac_list[j]
            data1 = combined_data[sensor1][sensor_type].dropna().values
            data2 = combined_data[sensor2][sensor_type].dropna().values
            
            # 确保两个数组长度一致，以较短的为准
            min_length = min(len(data1), len(data2))
            data1_aligned = data1[:min_length]
            data2_aligned = data2[:min_length]
            
            if len(data1_aligned) > 0 and len(data2_aligned) > 0:
                correlation, mse = calculate_consistency(data1_aligned, data2_aligned)
                if correlation > 0.95:
                    consistency_results.append((sensor1, sensor2, correlation, mse))
    
    # 找出相关系数大于0.95的传感器对
    high_correlation_sensors = set()
    for result in consistency_results:
        sensor1, sensor2, correlation, mse = result
        high_correlation_sensors.add(sensor1)
        high_correlation_sensors.add(sensor2)
    
    if not high_correlation_sensors:
        continue
    
    # 创建一个新的DataFrame，包含所有高相关性的传感器数据
    high_corr_df = pd.DataFrame({sensor: combined_data[sensor][sensor_type] for sensor in high_correlation_sensors})
    high_corr_df['Timestamp'] = combined_data[next(iter(high_correlation_sensors))]['Timestamp']
    
    # 找出基准传感器
    reference_sensor = find_reference_sensor(high_corr_df.drop(columns=['Timestamp']), high_correlation_sensors)
    
    # 以基准传感器为参考，对其他传感器进行调整
    adjusted_df = adjust_data(high_corr_df.drop(columns=['Timestamp']).copy(), reference_sensor)
    adjusted_df['Timestamp'] = high_corr_df['Timestamp']
    
    # 保存调整后的数据
    for sensor in adjusted_df.columns:
        if sensor != 'Timestamp':
            adjusted_data = combined_data[sensor].copy()
            adjusted_data[sensor_type] = adjusted_df[sensor]
            adjusted_csv_path = os.path.join(adjusted_csv_folder, f'{sensor}_adjusted.csv')
            adjusted_data.to_csv(adjusted_csv_path, index=False)
    
    # 绘制调整后的数据图像
    renamed_sensor_type = sensor_rename_map.get(sensor_type, sensor_type)
    plot_adjusted_data(renamed_sensor_type, combined_data, adjusted_df, output_folder)

print(f"All adjusted data saved to {adjusted_csv_folder} and plots saved to {output_folder}.")
