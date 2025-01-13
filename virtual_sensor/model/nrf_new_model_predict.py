import tensorflow as tf
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# 数据文件路径
data_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/test/test.csv"
tflite_model_output_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/new_model.tflite"
scaler_params_output_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/co_ppm_merged_scaler_params.csv"

# 加载数据
data = pd.read_csv(data_path)

# 确保数据包含必要的列
if 'label' not in data.columns or 'eCO2' not in data.columns:
    raise ValueError("Data must contain 'eCO2' and 'label' columns.")

# 分离特征和标签
X = data[['eCO2']].values
y = data['label'].values

# 数据分割（训练集和测试集）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 数据标准化
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# 保存标准化参数
scaler_params = pd.DataFrame({'mean': scaler.mean_, 'scale': scaler.scale_})
scaler_params.to_csv(scaler_params_output_path, index=False)
print(f"Scaler parameters saved to {scaler_params_output_path}")

# 构建模型
model = tf.keras.Sequential([
    tf.keras.layers.Input(shape=(1,)),  # 输入层，1个特征
    tf.keras.layers.Dense(16, activation='relu'),  # 隐藏层
    tf.keras.layers.Dense(8, activation='relu'),   # 隐藏层
    tf.keras.layers.Dense(len(np.unique(y)), activation='softmax')  # 输出层，分类数为标签的唯一值数量
])

# 编译模型
model.compile(optimizer='adam',
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

# 训练模型
model.fit(X_train_scaled, y_train, epochs=50, batch_size=16, validation_split=0.2)

# 评估模型
loss, accuracy = model.evaluate(X_test_scaled, y_test)
print(f"Test Loss: {loss:.4f}")
print(f"Test Accuracy: {accuracy:.4f}")

# 保存模型为 TensorFlow Lite 格式
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

# 保存 TFLite 模型
with open(tflite_model_output_path, 'wb') as f:
    f.write(tflite_model)
print(f"TFLite model saved to {tflite_model_output_path}")