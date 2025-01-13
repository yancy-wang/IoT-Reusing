import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# 数据路径
device_data_directory = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/wio_data/wio_cali_data"
thunderboard_directory = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/tbs2data/tbs2_cali_data"
output_pdf = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/sensor_data_comparison_with_thunderboard.pdf"

# 获取所有 Wio 传感器的CSV文件
device_csv_files = [os.path.join(device_data_directory, f) for f in os.listdir(device_data_directory) if f.endswith('.csv')]
# 获取 Thunderboard Sense 2 的CSV文件
thunderboard_csv_files = [os.path.join(thunderboard_directory, f) for f in os.listdir(thunderboard_directory) if f.endswith('.csv')]

# 定义传感器类型
sensor_types = ['Temperature', 'Humidity', 'Sound', 'Light', 'VOCs']

# 提取所有 MAC 地址，排除要移除的 MAC 地址，并重新生成映射
thunderboard_mac_set = set(os.path.basename(f).split('_')[0] for f in thunderboard_csv_files if "90:FD:9F:7B:84:FD" not in f)
thunderboard_mac_map = {mac: f"Thunderboard{index+1} ({mac})" for index, mac in enumerate(thunderboard_mac_set)}

# 读取 Thunderboard Sense 2 的数据
thunderboard_dfs = []
for file in thunderboard_csv_files:
    mac = os.path.basename(file).split('_')[0]
    
    # 过滤掉 MAC 地址为 90:FD:9F:7B:84:FD 的数据
    if mac == "90:FD:9F:7B:84:FD":
        continue
    
    df = pd.read_csv(file)
    
    # 自动推断时间戳格式
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df['Device'] = thunderboard_mac_map[mac]  # 根据 MAC 地址命名设备，包含编号和MAC
    thunderboard_dfs.append(df)

thunderboard_df = pd.concat(thunderboard_dfs)

# 统一列名
thunderboard_df.rename(columns={
    'Temperature (°C)': 'Temperature',
    'Humidity (%)': 'Humidity',
    'Sound Level (dB)': 'Sound',
    'Ambient Light (lux)': 'Light',
    'VOCs (ppb)': 'VOCs'
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

# 手动指定具有较大区分度的颜色列表
distinct_colors = [
    "#1f77b4",  # 蓝色
    "#ff7f0e",  # 橙色
    "#2ca02c",  # 绿色
    "#d62728",  # 红色
    "#9467bd",  # 紫色
    "#8c564b",  # 棕色
    "#e377c2",  # 粉色
    "#7f7f7f",  # 灰色
    "#bcbd22",  # 橄榄绿
    "#17becf",  # 青色
]

# 为每个 Thunderboard 和 Wio 设备分配颜色，确保颜色区分度大
color_map = {}
index = 0

# 为 Thunderboard 设备分配颜色
for device in thunderboard_mac_map.values():
    color_map[device] = distinct_colors[index % len(distinct_colors)]  # 从颜色列表中分配
    index += 1

# 为 Wio 设备分配颜色
for device in wio_device_map.values():
    color_map[device] = distinct_colors[index % len(distinct_colors)]
    index += 1

# 使用 groupby 按每分钟的时间间隔分组并计算平均值，同时保留 'Device' 列
def group_and_average(df):
    df['Timestamp'] = df['Timestamp'].dt.floor('min')  # 将时间戳向下取整到分钟
    numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns  # 只选择数值列
    grouped_df = df.groupby(['Timestamp', 'Device'])[numeric_cols].mean().reset_index()  # 按时间戳和设备分组，并计算平均值
    return grouped_df

# 对 Thunderboard 数据进行分组和平均处理
thunderboard_df = group_and_average(thunderboard_df)

# 获取 Thunderboard Sense 2 数据的时间范围并限制到 9月25日 17:00
start_time = thunderboard_df['Timestamp'].min()
end_time = pd.to_datetime('2024-09-25 17:00:00')  # 将时间限制到9月25日 17:00

# 平滑处理的函数
def smooth_data(data, window_size=10):
    return data.rolling(window=window_size, min_periods=1).mean()

# 过滤 Thunderboard 数据到 9月25日 17:00 之前
thunderboard_df = thunderboard_df[(thunderboard_df['Timestamp'] >= start_time) & (thunderboard_df['Timestamp'] <= end_time)]

# 将 Wio 数据中的声级 (mV) 转换为 dB
def convert_mv_to_db(mv_data, v_ref=1.0):
    """
    将毫伏转换为分贝，使用公式 20 * log10(mv / v_ref)
    :param mv_data: Wio 数据中的声级列 (mV)
    :param v_ref: 参考电压，默认为 1 mV
    :return: 转换为 dB 的数据
    """
    return 20 * np.log10(mv_data / v_ref)

# 绘制图表
with PdfPages(output_pdf) as pdf:
    for sensor_type in sensor_types:
        plt.figure(figsize=(10, 6))

        # 绘制 Thunderboard Sense 2 的平滑数据
        for device, group in thunderboard_df.groupby('Device'):
            smoothed_data = smooth_data(group[sensor_type])  # 对数据进行平滑处理
            plt.plot(group['Timestamp'], smoothed_data, label=device, color=color_map[device])

        # 绘制 Wio 传感器的数据
        for device_id, files in device_data.items():
            combined_df = pd.concat([pd.read_csv(f) for f in files])
            combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'], errors='coerce')

            # 手动添加 'Device' 列
            device_name = wio_device_map[device_id]
            combined_df['Device'] = device_name

            # 进行分组和平均处理
            combined_df = group_and_average(combined_df)
            
            # 过滤 Wio 数据，使其与 Thunderboard 的时间范围一致，并限制到 9月25日 17:00
            filtered_wio_df = combined_df[(combined_df['Timestamp'] >= start_time) & (combined_df['Timestamp'] <= end_time)]

            # 如果是声级传感器，将 mV 数据转换为 dB
            if sensor_type == 'Sound':
                filtered_wio_df[sensor_type] = convert_mv_to_db(filtered_wio_df[sensor_type])

            x_data = filtered_wio_df['Timestamp']
            y_data = filtered_wio_df[sensor_type]
            
            plt.plot(x_data, y_data, label=device_name, color=color_map[device_name])
        
        plt.xlabel("Time")
        plt.ylabel(sensor_type)
        plt.title(f"{sensor_type} Data Comparison: Wio vs Thunderboard Sense 2 (Smoothed)")
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        pdf.savefig()
        plt.close()

    # 单独绘制 Thunderboard Sense 2 的 VOC 数据，不包括 Wio 数据
    plt.figure(figsize=(10, 6))
    for device, group in thunderboard_df.groupby('Device'):
        smoothed_data = smooth_data(group['VOCs'])  # 对 VOC 数据进行平滑处理
        plt.plot(group['Timestamp'], smoothed_data, label=device, color=color_map[device])

    plt.xlabel("Time")
    plt.ylabel("VOCs")
    plt.title("VOC Data Comparison: Thunderboard Sense 2 Only (Smoothed)")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

print(f"All plots saved to {output_pdf}.")
