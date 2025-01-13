import json
from datetime import datetime
import pandas as pd

# 加载 JSON 文件
file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_wio/wio-2-test_live_data.json"
with open(file_path, "r") as file:
    data = json.load(file)

# 初始化数据列表
latency_results = []

# 解析和计算延迟
for entry in data:
    try:
        # 获取时间字段
        received_at = entry["data"]["uplink_message"]["received_at"]
        time = entry["time"]

        # 修正时间字符串，裁剪小数点后多余的部分
        if "Z" in received_at:
            received_at = received_at[:-1]  # 移除 'Z'
        if "Z" in time:
            time = time[:-1]  # 移除 'Z'

        # 裁剪到最多 6 个小数位
        if "." in received_at:
            received_at = received_at.split(".")[0] + "." + received_at.split(".")[1][:6]
        if "." in time:
            time = time.split(".")[0] + "." + time.split(".")[1][:6]

        # 转换为 datetime 对象
        received_at_dt = datetime.strptime(received_at, "%Y-%m-%dT%H:%M:%S.%f")
        time_dt = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S.%f")

        # 计算延迟
        latency = (time_dt - received_at_dt).total_seconds()

        # 保存结果
        latency_results.append({
            "Message ID": entry["unique_id"],
            "Received At": received_at,
            "Processed At": time,
            "Latency (s)": latency
        })

    except KeyError as e:
        print(f"Missing key in entry: {e}, skipping entry.")
        continue
    except ValueError as e:
        print(f"ValueError in parsing dates: {e}, skipping entry.")
        continue

# 检查是否有结果
if latency_results:
    # 将结果保存为 DataFrame
    df = pd.DataFrame(latency_results)

    # 保存为 CSV 文件
    output_csv_path = "/Users/wangyangyang/Desktop/Finland/summer_job/ubikampus/latency/scenario_wio/wio_latency.csv"
    df.to_csv(output_csv_path, index=False)

    print(f"Latency results saved to {output_csv_path}")
else:
    print("No valid entries found to calculate latency.")
