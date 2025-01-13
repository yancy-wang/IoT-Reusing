import os
import pandas as pd

# 指定包含 Normal 开头文件的文件夹路径
folder_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen"  # 替换为实际的 t2 文件夹路径
output_file = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/t2/tbs2_merged.csv"  # 合并后的输出文件路径

# 获取所有以 Normal 开头的文件
csv_files = [f for f in os.listdir(folder_path) if f.startswith("thunderboard") and f.endswith(".csv")]

# 按文件名中时间排序
csv_files.sort()

# 合并所有文件
data_frames = []
for csv_file in csv_files:
    file_path = os.path.join(folder_path, csv_file)
    df = pd.read_csv(file_path)  # 假设 CSV 文件有标题行
    data_frames.append(df)

# 将所有数据帧合并为一个大的数据帧
merged_df = pd.concat(data_frames, ignore_index=True)

# 保存到新的 CSV 文件
merged_df.to_csv(output_file, index=False)

print(f"合并完成，文件已保存到 {output_file}")