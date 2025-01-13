import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import time
import psutil  # For CPU and memory monitoring
import os

print(f"Current Process ID: {os.getpid()}")

# 文件路径
tflite_model_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/co_ppm_merged_eco2_model.tflite"
scaler_params_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/co_ppm_merged_scaler_params.csv"
test_data_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"

# 加载标准化参数
scaler_params = pd.read_csv(scaler_params_path)
scaler = StandardScaler()
scaler.mean_ = scaler_params['mean'].values
scaler.scale_ = scaler_params['scale'].values

# 加载测试数据
test_data = pd.read_csv(test_data_path)

# 确保测试数据中包含真实标签列 'label'
if 'label' not in test_data.columns:
    raise ValueError("Test data must contain 'label' column for accuracy calculation.")

X_test = test_data[['eCO2']].values
y_true = test_data['label'].values  # 真实标签

# 标准化数据
X_test_scaled = scaler.transform(X_test)

# 加载 TFLite 模型
interpreter = tf.lite.Interpreter(model_path=tflite_model_path)
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# 初始化性能测量变量
inference_times = []
cpu_usages = []
absolute_memory_usages = []  # 保存实际内存值

# 获取当前进程
process = psutil.Process(os.getpid())

# 执行推理
predicted_labels = []
overall_cpu_start = psutil.cpu_percent(interval=None)  # 总体 CPU 开始使用率
overall_memory_start = process.memory_info().rss / 1024  # 总体内存开始使用量 (KB)

for input_value in X_test_scaled:
    # 记录开始时间和系统资源状态
    start_time = time.time()
    cpu_start = psutil.cpu_percent(interval=None)

    # 执行模型推理
    input_data = np.array([input_value], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_label = np.argmax(output_data)
    predicted_labels.append(predicted_label)

    # 记录结束时间和系统资源状态
    end_time = time.time()
    cpu_end = psutil.cpu_percent(interval=None)
    current_memory_usage = process.memory_info().rss / 1024  # 实际内存使用 (KB)

    # 计算推理时间和资源使用
    inference_time = (end_time - start_time) * 1e6  # 转换为微秒
    cpu_usage = (cpu_start + cpu_end) / 2  # 平均 CPU 使用率

    inference_times.append(inference_time)
    cpu_usages.append(cpu_usage)
    absolute_memory_usages.append(current_memory_usage)  # 保存实际内存值

    print(f"Inference Time: {inference_time:.2f} us, CPU Usage: {cpu_usage:.2f}%, Memory Usage: {current_memory_usage:.2f} KB")
    
    # 增加 0.1 秒延时
    time.sleep(0.1)

# 记录推理后的总体资源使用
overall_cpu_end = psutil.cpu_percent(interval=None)
overall_memory_end = process.memory_info().rss / 1024  # 总体内存结束使用量 (KB)

# 保存预测结果
test_data['Predicted_Label'] = predicted_labels
test_data['Inference_Time_us'] = inference_times
test_data['CPU_Usage_%'] = cpu_usages
test_data['Memory_Usage_KB'] = absolute_memory_usages
output_file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/test_predictions_with_performance.csv"
test_data.to_csv(output_file_path, index=False)
print(f"Predictions and performance metrics saved to {output_file_path}")

# 计算性能统计
average_inference_time = sum(inference_times) / len(inference_times)
average_cpu_usage = (overall_cpu_start + overall_cpu_end) / 2  # 整体平均 CPU 使用率
average_memory_usage = sum(absolute_memory_usages) / len(absolute_memory_usages)  # 平均内存使用

print(f"Average Inference Time: {average_inference_time:.2f} us")
print(f"Average CPU Usage (Overall): {average_cpu_usage:.2f}%")
print(f"Average Memory Usage: {average_memory_usage:.2f} KB")
print(f"Total Memory Used: {overall_memory_end:.2f} KB")

# 计算准确率
accuracy = accuracy_score(y_true, predicted_labels)
print(f"Accuracy: {accuracy:.4f}")

# 生成分类报告
report = classification_report(y_true, predicted_labels)
print("Classification Report:\n", report)