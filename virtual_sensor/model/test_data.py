import pandas as pd

# 加载数据
file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/co_ppm_merged.csv"  # 替换为本地文件路径
df = pd.read_csv(file_path)

# 筛选 eCO2 在 400 到 2000 范围内的数据
filtered_df = df[(df['eCO2'] >= 400) & (df['eCO2'] <= 2000)]

# 随机抽取 1000 条数据
sampled_df = filtered_df.sample(n=1000, random_state=42)

# 仅保留 eCO2 和 label 列
output_df = sampled_df[['eCO2', 'label']]

# 保存到本地 test.csv 文件
output_file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"
output_df.to_csv(output_file_path, index=False)

print(f"文件已保存至: {output_file_path}")