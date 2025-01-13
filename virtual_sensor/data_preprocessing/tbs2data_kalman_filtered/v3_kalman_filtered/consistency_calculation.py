import os
import pandas as pd
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages
from urllib.parse import unquote
import matplotlib.pyplot as plt
from matplotlib.table import Table, Cell

def calculate_consistency(data1, data2):
    valid_indices = ~np.isnan(data1) & ~np.isnan(data2)
    data1 = data1[valid_indices]
    data2 = data2[valid_indices]
    correlation = np.corrcoef(data1, data2)[0, 1] if len(data1) > 0 and len(data2) > 0 else np.nan
    mse = np.mean((data1 - data2) ** 2) if len(data1) > 0 and len(data2) > 0 else np.nan
    return correlation, mse

# 定义输入和输出目录
input_folder = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v3_kalman_filtered"
output_pdf = "/Users/wangyangyang/Desktop/Finland/summer_job/data_all/tbs2data_kalman_filtered/v3_kalman_filtered/Kalman_v3_filtered_comparison.pdf"

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
    combined_df['Index'] = combined_df.index
    combined_data[mac] = combined_df

# 定义颜色映射表
color_map = {
    '00:0D:6F:20:D3:F3': '#1f77b4',  # Blue
    '00:0D:6F:20:D4:96': '#ff7f0e',  # Orange
    '90:FD:9F:7B:81:06': '#d62728',  # Red
    '90:FD:9F:7B:82:50': '#8c564b',  # Brown
    '90:FD:9F:7B:83:D1': '#e377c2',  # Pink
    '90:FD:9F:7B:83:D6': '#bcbd22',  # Yellow-green
    '90:FD:9F:7B:84:67': '#17becf'   # Cyan
}

# 定义MAC地址序号映射表
mac_sequence = {
    '00:0D:6F:20:D3:F3': 11,
    '00:0D:6F:20:D4:96': 14,
    '90:FD:9F:7B:81:06': 4,
    '90:FD:9F:7B:82:50': 13,
    '90:FD:9F:7B:83:D1': 9,
    '90:FD:9F:7B:83:D6': 3,
    '90:FD:9F:7B:84:67': 10
}

# 保存所有相似度结果
all_consistency_results = []

# 计算每对设备之间的相似度
for sensor_type in sensor_types:
    mac_list = list(combined_data.keys())
    consistency_results = []
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
                mac1_with_sequence = f"{mac1}({mac_sequence[mac1]})"
                mac2_with_sequence = f"{mac2}({mac_sequence[mac2]})"
                consistency_results.append({
                    'MAC1': mac1_with_sequence,
                    'MAC2': mac2_with_sequence,
                    'Correlation': correlation,
                    'MSE': mse
                })
    
    if consistency_results:
        all_consistency_results.append((sensor_type, consistency_results))

# 仅当有相似度结果时才创建PDF文件
if all_consistency_results:
    with PdfPages(output_pdf) as pdf:
        for sensor_type, consistency_results in all_consistency_results:
            df_results = pd.DataFrame(consistency_results)
            fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 纸大小
            ax.axis('off')

            table = Table(ax, bbox=[0, 0, 1, 1])

            # 添加表头
            ncols = len(df_results.columns)
            nrows = len(df_results) + 1
            for i, col in enumerate(df_results.columns):
                table.add_cell(0, i, width=1/ncols, height=1/nrows, text=col, loc='center', facecolor='lightgrey')

            # 添加数据
            for row_idx, row in df_results.iterrows():
                for col_idx, value in enumerate(row):
                    fontcolor = 'black'
                    if col_idx == 2 and value > 0.95:  # High correlation
                        fontcolor = 'green'
                    if col_idx == 3 and value < 0.2:  # Low MSE
                        fontcolor = 'green'
                    if col_idx == 0:  # MAC1
                        mac_original = row['MAC1'].split('(')[0]
                        fontcolor = color_map.get(mac_original, 'black')
                    if col_idx == 1:  # MAC2
                        mac_original = row['MAC2'].split('(')[0]
                        fontcolor = color_map.get(mac_original, 'black')
                    table.add_cell(row_idx + 1, col_idx, width=1/ncols, height=1/nrows, text=str(value), loc='center', facecolor='white')
                    table[(row_idx + 1, col_idx)].get_text().set_color(fontcolor)

            ax.add_table(table)
            ax.set_title(f"{sensor_type} Consistency Results", fontweight="bold")
            pdf.savefig(fig)
            plt.close()
    print(f"All consistency calculations saved to {output_pdf}.")
else:
    print("No consistency calculations were found.")
