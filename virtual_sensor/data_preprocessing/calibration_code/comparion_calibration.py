import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import pearsonr
from sklearn.metrics import mean_absolute_error

# 数据路径
device_data_directory = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/wio_data/wio_cali_data"
thunderboard_directory = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/tbs2data/tbs2_cali_data"
output_pdf = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/sensor_data_calibration.pdf"
intercept_output_file = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/sensor_intercepts_mae.csv"

# 获取所有 Wio 传感器的CSV文件
device_csv_files = [os.path.join(device_data_directory, f) for f in os.listdir(device_data_directory) if f.endswith('.csv')]
# 获取 Thunderboard Sense 2 的CSV文件
thunderboard_csv_files = [os.path.join(thunderboard_directory, f) for f in os.listdir(thunderboard_directory) if f.endswith('.csv')]

# 定义传感器类型
sensor_types = ['Temperature', 'Humidity', 'Light']

# 设置时间过滤条件
cutoff_time = pd.to_datetime('2024-09-25 17:00:00')

# 提取所有 MAC 地址，重新生成映射并排除指定的 MAC 地址
thunderboard_mac_set = set(os.path.basename(f).split('_')[0] for f in thunderboard_csv_files if "90:FD:9F:7B:84:FD" not in f)
thunderboard_mac_map = {mac: f"Thunderboard{index+1}" for index, mac in enumerate(thunderboard_mac_set)}

# 读取 Thunderboard Sense 2 的数据并生成统一 DataFrame
thunderboard_dfs = []
for file in thunderboard_csv_files:
    mac = os.path.basename(file).split('_')[0]
    
    # 跳过指定的 MAC 地址
    if mac == "90:FD:9F:7B:84:FD":
        continue
    
    df = pd.read_csv(file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df[df['Timestamp'] <= cutoff_time]  # 限制时间在 9.25 17:00:00 之前
    df['Device'] = thunderboard_mac_map[mac]  # 根据 MAC 地址命名设备
    thunderboard_dfs.append(df)

thunderboard_df = pd.concat(thunderboard_dfs)

# 统一列名
thunderboard_df.rename(columns={
    'Temperature (°C)': 'Temperature',
    'Humidity (%)': 'Humidity',
    'Ambient Light (lux)': 'Light'
}, inplace=True)

# 分配 Wio 数据文件 (Wio1, Wio2, Wio3)
device_data = {}
for csv_file in device_csv_files:
    file_name = os.path.basename(csv_file)
    device_id = file_name.split('_')[0]
    if device_id not in device_data:
        device_data[device_id] = []
    device_data[device_id].append(csv_file)

wio_device_map = {'1': 'Wio1', '2': 'Wio2', '3': 'Wio3'}  # 区分Wio设备

# 读取 Wio 数据并生成统一 DataFrame
wio_dfs = []
for device_id, files in device_data.items():
    combined_df = pd.concat([pd.read_csv(f) for f in files])
    combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'], errors='coerce')
    combined_df = combined_df[combined_df['Timestamp'] <= cutoff_time]  # 限制时间在 9.25 17:00:00 之前
    combined_df['Device'] = wio_device_map[device_id]
    wio_dfs.append(combined_df)

wio_df = pd.concat(wio_dfs)
wio_devices = wio_df['Device'].unique()

# 合并 Thunderboard 和 Wio 数据
combined_df = pd.concat([thunderboard_df, wio_df])

# 使用 groupby 按每分钟的时间间隔分组并计算平均值，同时保留 'Device' 列
def group_and_average(df):
    df['Timestamp'] = df['Timestamp'].dt.floor('min')  # 将时间戳向下取整到分钟
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns  # 只选择数值列
    grouped_df = df.groupby(['Timestamp', 'Device'])[numeric_cols].mean().reset_index()  # 按时间戳和设备分组，并计算平均值
    return grouped_df

# 对数据进行分组和平均处理
combined_df = group_and_average(combined_df)

# 计算相关性并找到可以校准的传感器
def calculate_correlations(df, sensor_type):
    devices = df['Device'].unique()
    correlation_matrix = pd.DataFrame(index=devices, columns=devices)
    for i, device_1 in enumerate(devices):
        for j, device_2 in enumerate(devices):
            if i >= j:  # 只计算上三角矩阵
                continue
            data_1 = df[df['Device'] == device_1][sensor_type].dropna()
            data_2 = df[df['Device'] == device_2][sensor_type].dropna()
            min_length = min(len(data_1), len(data_2))
            if min_length > 0:
                corr, _ = pearsonr(data_1[:min_length], data_2[:min_length])
                correlation_matrix.loc[device_1, device_2] = corr
                correlation_matrix.loc[device_2, device_1] = corr
    return correlation_matrix

# 找到基准传感器（相关性中位数传感器）
def find_reference_device(correlation_matrix, wio_devices):
    median_correlation = correlation_matrix.loc[wio_devices, wio_devices].median(axis=1)
    reference_device = median_correlation.idxmax()  # 中位数最大值作为基准
    return reference_device

# 对可校准的传感器进行加上截距校准
def calibrate_sensors(df, reference_device, sensor_type):
    intercepts = {}
    for device in df['Device'].unique():
        if device == reference_device:
            intercepts[device] = 0  # 基准设备不需要校准
        else:
            reference_data = df[df['Device'] == reference_device][sensor_type]
            device_data = df[df['Device'] == device][sensor_type]
            intercept = reference_data.mean() - device_data.mean()  # 计算截距
            df.loc[df['Device'] == device, sensor_type] += intercept
            intercepts[device] = intercept
    return df, intercepts

# 绘制校准前后对比图并保存PDF
def plot_comparison(df, sensor_type, intercepts, reference_device):
    plt.figure(figsize=(10, 6))
    for device in df['Device'].unique():
        data = df[df['Device'] == device]
        plt.plot(data['Timestamp'], data[sensor_type], label=f'{device} (Intercept: {intercepts.get(device, 0):.2f})')
    
    plt.xlabel("Time")
    plt.ylabel(sensor_type)
    plt.title(f"{sensor_type} Data Comparison (Calibrated, Reference: {reference_device})")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

# 计算 MAE (均方误差)
def calculate_mae(df, reference_device, sensor_type):
    mae_values = {}
    reference_data = df[df['Device'] == reference_device][sensor_type].dropna()
    for device in df['Device'].unique():
        if device == reference_device:
            continue
        device_data = df[df['Device'] == device][sensor_type].dropna()
        min_length = min(len(reference_data), len(device_data))
        mae = mean_absolute_error(reference_data[:min_length], device_data[:min_length])
        mae_values[device] = mae
    return mae_values



# 主函数执行校准过程
with PdfPages(output_pdf) as pdf:
    intercepts_records = []
    mae_records = []

    for sensor_type in sensor_types:
        # 计算相关性前，先绘制校准前的对比图
        plt.figure(figsize=(10, 6))
        for device in combined_df['Device'].unique():
            data = combined_df[combined_df['Device'] == device]
            plt.plot(data['Timestamp'], data[sensor_type], label=f'{device} (Before Calibration)')
        
        plt.xlabel("Time")
        plt.ylabel(sensor_type)
        plt.title(f"{sensor_type} Data Comparison (Before Calibration)")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # 保存校准前的图像到 PDF
        pdf.savefig()
        plt.close()



        # 计算相关性
        correlation_matrix = calculate_correlations(combined_df, sensor_type)
        # 选择基准传感器
        reference_device = find_reference_device(correlation_matrix, wio_devices)
        # 对数据进行校准
        combined_df, intercepts = calibrate_sensors(combined_df, reference_device, sensor_type)
        # 记录截距
        for device, intercept in intercepts.items():
            intercepts_records.append({
                'Sensor Type': sensor_type,
                'Device': device,
                'Intercept': intercept
            })
        # 计算 MAE 并记录
        mae_values = calculate_mae(combined_df, reference_device, sensor_type)
        for device, mae in mae_values.items():
            mae_records.append({
                'Sensor Type': sensor_type,
                'Device': device,
                'MAE': mae
            })
        # 绘制校准前后对比图
        plot_comparison(combined_df, sensor_type, intercepts, reference_device)
        pdf.savefig()
        plt.close()

# 保存截距记录和MAE记录到 CSV 文件
intercepts_df = pd.DataFrame(intercepts_records)
mae_df = pd.DataFrame(mae_records)

# 合并拦截记录和MAE记录，并保存为一个 CSV 文件
final_df = pd.merge(intercepts_df, mae_df, on=['Sensor Type', 'Device'], how='left')
final_df.to_csv(intercept_output_file, index=False)

print(f"All plots and intercept values saved. PDF and CSV are generated.")
