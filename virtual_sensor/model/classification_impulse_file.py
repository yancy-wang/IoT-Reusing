import os
import pandas as pd

# 定义文件路径和目标输出路径
base_dir = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3'
output_dir = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files'

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 目标列和相应的字段名称映射
target_columns = {
    "co_ppm": "co_ppm",
    "no2_ppb": "no2_ppb",
    "nc_0p5_npcm3": "nc_0p5_npcm3",
    "nc_1p0_npcm3": "nc_1p0_npcm3",
    "nc_2p5_npcm3": "nc_2p5_npcm3",
    "nc_4p0_npcm3": "nc_4p0_npcm3",
    "nc_10p0_npcm3": "nc_10p0_npcm3",
    "Mc_1p0_ugpm3": "Mc_1p0_ugpm3",
    "Mc_2p5_ugpm3": "Mc_2p5_ugpm3",
    "Mc_4p0_ugpm3": "Mc_4p0_ugpm3",
    "Mc_10p0_ugpm3": "Mc_10p0_ugpm3"
}

# 遍历每个目标列
for target, field_name in target_columns.items():
    merged_data = []  # 存储当前目标列的所有数据
    target_dir = os.path.join(base_dir, target)
    for level in range(3):  # 遍历0-9级别
        tbs2_file_path = os.path.join(target_dir, f"{target}_tbs2_level_{level}.csv")
        level_file_path = os.path.join(target_dir, f"{target}_level_{level}.csv")
        
        if os.path.exists(tbs2_file_path) and os.path.exists(level_file_path):
            # 读取Thunderboard Sense 2文件
            tbs2_data = pd.read_csv(tbs2_file_path)
            # 读取对应的目标列文件
            level_data = pd.read_csv(level_file_path)
            # 提取目标列数据
            if field_name in level_data.columns:
                tbs2_data[field_name] = level_data[field_name]
            # 添加label列
            tbs2_data['label'] = level
            # 删除包含空值的行
            tbs2_data = tbs2_data.dropna()
            # 添加到当前目标列的数据列表
            merged_data.append(tbs2_data)
    
    # 合并当前目标列的所有数据
    if merged_data:
        final_data = pd.concat(merged_data, ignore_index=True)
        # 保存到对应的目标文件
        output_file = os.path.join(output_dir, f"{target}_merged.csv")
        final_data.to_csv(output_file, index=False)
        print(f"Merged data for {target} saved to {output_file}")