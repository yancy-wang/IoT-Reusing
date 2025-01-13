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

def find_reference_mac(df, mac_list):
    df_filled = df.fillna(df.mean())
    mean_values = df_filled.mean(axis=1)
    distances = {mac: euclidean(mean_values, df_filled[mac]) for mac in mac_list}
    return min(distances, key=distances.get)

def adjust_data(df, reference_mac):
    adjustments = {mac: df[reference_mac].mean() - df[mac].mean() for mac in df.columns if mac != reference_mac}
    for mac, adjustment in adjustments.items():
        df[mac] += adjustment
    return df, adjustments

def plot_adjusted_data(sensor_type, adjusted_data, reference_mac, pdf, color_map):
    plt.figure(figsize=(10, 6))
    for mac in adjusted_data.columns:
        if mac != 'Timestamp':
            label = f'{mac} (Reference)' if mac == reference_mac else f'{mac}'
            plt.plot(adjusted_data['Timestamp'], adjusted_data[mac], label=label, color=color_map.get(mac, 'black'))
    plt.xlabel('Timestamp')
    plt.ylabel(sensor_type)
    plt.title(f'Adjusted {sensor_type} Data')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# 定义输入和输出目录
input_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_kalman_filtered"
output_pdf_path = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_calibration_intercept/adjusted_data_plots.pdf"
adjusted_csv_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_calibration_intercept"
intercept_file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v2_calibration_intercept/adjustments.csv"

# 定义颜色映射
color_map = {
    '00:0B:57:64:8C:41': '#1f77b4',  # Blue
    '00:0D:6F:20:D4:68': '#ff7f0e',  # Orange
    '90:FD:9F:7B:81:06': '#d62728',  # Red
    '90:FD:9F:7B:83:D6': '#8c564b',  # Brown
    '90:FD:9F:7B:84:EA': '#e377c2',  # Pink
    '90:FD:9F:7B:84:FD': '#bcbd22',  # Yellow-green
    '90:FD:9F:7B:85:2B': '#17becf'   # Cyan
}

# 确保输出文件夹存在
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
    if device_mac not in device_data:
        device_data[device_mac] = []
    device_data[device_mac].append(csv_file)

# 确保每个设备的文件按时间顺序排序
for mac in device_data:
    device_data[mac].sort()

# 读取第一个文件以获取传感器类型
sample_df = pd.read_csv(csv_files[0])
sensor_types = sample_df.columns[1:]  # 假设第一列是时间戳，剩下的是传感器类型

# 去掉'Timestamp'列
sensor_types = [sensor for sensor in sensor_types if sensor.lower() != 'timestamp']

# 合并每个设备的CSV文件，并给每个时间点按顺序编号
combined_data = {}
for mac, files in device_data.items():
    df_list = [pd.read_csv(f) for f in files]
    combined_df = pd.concat(df_list).sort_values('Timestamp').reset_index(drop=True)
    combined_df['Timestamp'] = pd.to_datetime(combined_df['Timestamp'])
    combined_df['Index'] = combined_df.index
    combined_data[mac] = combined_df

# 创建PDF文件并初始化调整记录
with PdfPages(output_pdf_path) as pdf:
    adjustments_records = []
    
    # 处理每个传感器项
    for sensor_type in sensor_types:
        mac_list = list(combined_data.keys())
        consistency_results = []
        
        # 计算每对设备之间的相似度
        for i in range(len(mac_list)):
            for j in range(i + 1, len(mac_list)):
                mac1 = mac_list[i]
                mac2 = mac_list[j]
                data1 = combined_data[mac1][sensor_type].dropna().values
                data2 = combined_data[mac2][sensor_type].dropna().values
                
                # 确保两个数组长度一致，以较短的为准
                min_length = min(len(data1), len(data2))
                data1_aligned = data1[:min_length]
                data2_aligned = data2[:min_length]
                
                if len(data1_aligned) > 0 and len(data2_aligned) > 0:
                    correlation, mse = calculate_consistency(data1_aligned, data2_aligned)
                    if correlation > 0.95:
                        consistency_results.append((mac1, mac2, correlation, mse))
        
        # 找出相关系数大于0.95的MAC对
        high_correlation_macs = set()
        for result in consistency_results:
            mac1, mac2, correlation, mse = result
            high_correlation_macs.add(mac1)
            high_correlation_macs.add(mac2)
        
        if not high_correlation_macs:
            continue
        
        # 创建一个新的DataFrame，包含所有高相关性的MAC数据
        high_corr_df = pd.DataFrame({mac: combined_data[mac][sensor_type] for mac in high_correlation_macs})
        high_corr_df['Timestamp'] = combined_data[next(iter(high_correlation_macs))]['Timestamp']
        
        # 找出基准MAC
        reference_mac = find_reference_mac(high_corr_df.drop(columns=['Timestamp']), high_correlation_macs)
        
        # 以基准MAC为参考，对其他MAC进行调整
        adjusted_df, adjustments = adjust_data(high_corr_df.drop(columns=['Timestamp']).copy(), reference_mac)
        adjusted_df['Timestamp'] = high_corr_df['Timestamp']
        
        # 保存调整记录
        for mac, adjustment in adjustments.items():
            adjustments_records.append({
                'Sensor': sensor_type,
                'MAC': mac,
                'Reference MAC': reference_mac,
                'Adjustment': adjustment
            })
        
        # 保存调整后的数据
        for mac in adjusted_df.columns:
            if mac != 'Timestamp':
                adjusted_data = combined_data[mac].copy()
                adjusted_data[sensor_type] = adjusted_df[mac]
                adjusted_csv_path = os.path.join(adjusted_csv_folder, f'{mac}_adjusted.csv')
                adjusted_data.to_csv(adjusted_csv_path, index=False)
        
        # 绘制调整后的数据图像
        plot_adjusted_data(sensor_type, adjusted_df, reference_mac, pdf, color_map)

# 保存调整记录到CSV文件
adjustments_df = pd.DataFrame(adjustments_records)
adjustments_df.to_csv(intercept_file_path, index=False)

print(f"All adjusted data saved to {adjusted_csv_folder} and plots saved to {output_pdf_path}. Adjustments saved to {intercept_file_path}.")
