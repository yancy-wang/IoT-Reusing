import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

print(f"TensorFlow version = {tf.__version__}\n")

# 固定随机种子，确保结果可复现
SEED = 1337
np.random.seed(SEED)
tf.random.set_seed(SEED)

# 文件路径
l0_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/level0.csv"
l1_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/level1.csv"
l2_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/level2.csv"
tflite_model_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/co_ppm_level_model.tflite"
scaler_params_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/scaler_params.csv"
header_file_path = "/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/co_ppm/model.h"

# 类别定义
LEVELS = [
    {"name": "level0", "path": l0_path},
    {"name": "level1", "path": l1_path},
    {"name": "level2", "path": l2_path},
]
NUM_LEVELS = len(LEVELS)

# 创建One-Hot编码矩阵
ONE_HOT_ENCODED_LEVELS = np.eye(NUM_LEVELS)

inputs = []
outputs = []

# 读取各个level的数据并附上标签
for level_index, level in enumerate(LEVELS):
    print(f"Processing index {level_index} for level '{level['name']}'.")

    # 加载数据
    df = pd.read_csv(level['path'])
    df = df.dropna(subset=['eCO2'])  # 去除缺失值

    # 限定输入特征并附上标签
    for _, row in df.iterrows():
        inputs.append([row['eCO2']])
        outputs.append(ONE_HOT_ENCODED_LEVELS[level_index])

# 转换为numpy数组
inputs = np.array(inputs)
outputs = np.array(outputs)

print("Data set parsing and preparation complete.")

# 数据标准化
scaler = StandardScaler()
inputs_scaled = scaler.fit_transform(inputs)

# 保存标准化参数（供Arduino代码使用）
scaler_params = pd.DataFrame({'mean': scaler.mean_, 'scale': scaler.scale_})
scaler_params.to_csv(scaler_params_path, index=False)
print(f"Scaler parameters saved to: {scaler_params_path}")

# 随机化并分割数据
num_inputs = len(inputs_scaled)
randomize = np.arange(num_inputs)
np.random.shuffle(randomize)

inputs_scaled = inputs_scaled[randomize]
outputs = outputs[randomize]

TRAIN_SPLIT = int(0.6 * num_inputs)
TEST_SPLIT = int(0.2 * num_inputs + TRAIN_SPLIT)

inputs_train, inputs_test, inputs_validate = np.split(inputs_scaled, [TRAIN_SPLIT, TEST_SPLIT])
outputs_train, outputs_test, outputs_validate = np.split(outputs, [TRAIN_SPLIT, TEST_SPLIT])

print("Data set randomization and splitting complete.")

# 构建神经网络模型
model = tf.keras.Sequential([
    tf.keras.layers.Dense(8, activation='relu', input_shape=(1,)),
    tf.keras.layers.Dense(4, activation='relu'),
    tf.keras.layers.Dense(NUM_LEVELS, activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 训练模型
history = model.fit(inputs_train, outputs_train, epochs=100, batch_size=16, validation_data=(inputs_validate, outputs_validate))

# 绘制训练和验证的损失曲线
plt.rcParams["figure.figsize"] = (20, 10)
loss = history.history['loss']
val_loss = history.history['val_loss']
epochs = range(1, len(loss) + 1)

plt.plot(epochs, loss, 'g.', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

# 评估模型
test_loss, test_accuracy = model.evaluate(inputs_test, outputs_test)
print(f"Test Accuracy: {test_accuracy:.4f}")

# TensorFlow Lite模型转换
def representative_data_gen():
    for input_value in inputs_train:
        yield [np.array(input_value, dtype=np.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_data_gen
tflite_model = converter.convert()

# 保存TFLite模型
with open(tflite_model_path, "wb") as f:
    f.write(tflite_model)
print(f"TFLite model saved to {tflite_model_path}")

# 生成Arduino Header文件
import os
os.system(f"xxd -i {tflite_model_path} > {header_file_path}")
print(f"Header file '{header_file_path}' generated.")