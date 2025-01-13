import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import time
import tracemalloc  # 用于精确监控内存分配

# 文件路径
tflite_model_path = "/home/pi/mu_code/tf_model/co_ppm_merged_eco2_model.tflite"
scaler_params_path = "/home/pi/mu_code/tf_model/co_ppm_merged_scaler_params.csv"
test_data_path = "/home/pi/mu_code/tf_model/test.csv"

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
memory_usages = []

# 启动 tracemalloc
tracemalloc.start()

# 执行推理
predicted_labels = []

for input_value in X_test_scaled:
    # 记录开始时间和内存快照
    start_time = time.time()
    snapshot_start = tracemalloc.take_snapshot()

    # 执行模型推理
    input_data = np.array([input_value], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_label = np.argmax(output_data)
    predicted_labels.append(predicted_label)

    # 记录结束时间和内存快照
    end_time = time.time()
    snapshot_end = tracemalloc.take_snapshot()

    # 比较内存快照，计算内存变化
    stats = snapshot_end.compare_to(snapshot_start, 'lineno')
    memory_diff = sum(stat.size_diff for stat in stats) / 1024  # 转换为 KB

    # 记录推理时间
    inference_time = (end_time - start_time) * 1e6  # 转换为微秒
    inference_times.append(inference_time)
    memory_usages.append(memory_diff)

    print(f"Inference Time: {inference_time:.2f} us, Memory Change: {memory_diff:.2f} KB")
    time.sleep(0.1)

# 停止 tracemalloc
tracemalloc.stop()

# 保存预测结果
test_data['Predicted_Label'] = predicted_labels
test_data['Inference_Time_us'] = inference_times
test_data['Memory_Usage_KB'] = memory_usages
output_file_path = "/home/pi/mu_code/tf_model/test_predictions_with_performance.csv"
test_data.to_csv(output_file_path, index=False)
print(f"Predictions and performance metrics saved to {output_file_path}")

# 计算性能统计
average_inference_time = sum(inference_times) / len(inference_times)
average_memory_usage = sum(memory_usages) / len(memory_usages)  # 平均内存变化

print(f"Average Inference Time: {average_inference_time:.2f} us")
print(f"Average Memory Usage Change: {average_memory_usage:.2f} KB")

# 计算准确率
accuracy = accuracy_score(y_true, predicted_labels)
print(f"Accuracy: {accuracy:.4f}")

# 生成分类报告
report = classification_report(y_true, predicted_labels)
print("Classification Report:\n", report)