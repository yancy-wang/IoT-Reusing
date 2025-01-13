import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from sklearn.model_selection import train_test_split

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

# 执行 TensorFlow Lite 推理
predicted_labels_tf = []
for input_value in X_test_scaled:
    input_data = np.array([input_value], dtype=np.float32)
    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])
    predicted_label = np.argmax(output_data)
    predicted_labels_tf.append(predicted_label)

# 计算 TensorFlow Lite 模型的准确率
accuracy_tf = accuracy_score(y_true, predicted_labels_tf)
print(f"TensorFlow Lite Model Accuracy: {accuracy_tf:.5f}")
print("Classification Report for TensorFlow Lite:\n", classification_report(y_true, predicted_labels_tf))

# 分割数据集用于其他模型的训练
X_train, X_val, y_train, y_val = train_test_split(X_test_scaled, y_true, test_size=0.2, random_state=42)

# Random Forest
rf_model = RandomForestClassifier(random_state=42)
rf_model.fit(X_train, y_train)
predicted_labels_rf = rf_model.predict(X_val)
accuracy_rf = accuracy_score(y_val, predicted_labels_rf)
print(f"Random Forest Accuracy: {accuracy_rf:.5f}")
print("Classification Report for Random Forest:\n", classification_report(y_val, predicted_labels_rf))

# XGBoost
xgb_model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss', random_state=42)
xgb_model.fit(X_train, y_train)
predicted_labels_xgb = xgb_model.predict(X_val)
accuracy_xgb = accuracy_score(y_val, predicted_labels_xgb)
print(f"XGBoost Accuracy: {accuracy_xgb:.5f}")
print("Classification Report for XGBoost:\n", classification_report(y_val, predicted_labels_xgb))

# LightGBM
lgbm_model = LGBMClassifier(random_state=42)
lgbm_model.fit(X_train, y_train)
predicted_labels_lgbm = lgbm_model.predict(X_val)
accuracy_lgbm = accuracy_score(y_val, predicted_labels_lgbm)
print(f"LightGBM Accuracy: {accuracy_lgbm:.5f}")
print("Classification Report for LightGBM:\n", classification_report(y_val, predicted_labels_lgbm))

# 保存所有模型的结果到 CSV 文件
results = {
    "Model": ["TensorFlow Lite", "Random Forest", "XGBoost", "LightGBM"],
    "Accuracy": [accuracy_tf, accuracy_rf, accuracy_xgb, accuracy_lgbm]
}

results_df = pd.DataFrame(results)
results_output_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/model_comparison_results.csv"
results_df.to_csv(results_output_path, index=False)
print(f"Model comparison results saved to {results_output_path}")