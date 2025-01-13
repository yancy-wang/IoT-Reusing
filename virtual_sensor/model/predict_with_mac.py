import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# 文件路径
tflite_model_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/new_model.tflite"
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

# 执行推理
predicted_labels = []
for input_value in X_test_scaled:
    input_data = np.array([input_value], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_label = np.argmax(output_data)
    predicted_labels.append(predicted_label)

# 保存预测结果
test_data['Predicted_Label'] = predicted_labels
output_file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/test_predictions_original.csv"
test_data.to_csv(output_file_path, index=False)
print(f"Predictions saved to {output_file_path}")

# 计算准确率
accuracy = accuracy_score(y_true, predicted_labels)
print(f"Accuracy: {accuracy:.4f}")

# 生成分类报告
report = classification_report(y_true, predicted_labels)
print("Classification Report:\n", report)