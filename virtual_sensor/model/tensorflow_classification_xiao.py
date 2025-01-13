import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
from fpdf import FPDF
import pandas as pd
import os

# 文件夹路径
folder_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files'
output_pdf_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files/classification_results_co_ppm.pdf'

# 初始化 PDF
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Classification Results Report (TFLite Model for co_ppm using eCO2)", ln=True, align='C')

# 遍历文件夹中的所有 CSV 文件
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv') and 'co_ppm' in file_name:  # 仅处理包含 'co_ppm' 的文件
        file_path = os.path.join(folder_path, file_name)

        # 加载数据
        data = pd.read_csv(file_path)
        
        # 确保 'label' 和特征 'eCO2' 存在
        if 'label' in data.columns and 'eCO2' in data.columns:
            X = data[['eCO2']]
            y = data['label']

            # 清理数据，确保 label 为整数型
            y = y.astype('int')
            
            # 自动获取类别数量
            num_classes = len(y.unique())

            # 数据标准化
            scaler = StandardScaler()
            X = scaler.fit_transform(X)

            # 数据分割
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 构建简单神经网络模型
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(16, activation='relu', input_shape=(X_train.shape[1],)),
                tf.keras.layers.Dense(8, activation='relu'),
                tf.keras.layers.Dense(num_classes, activation='softmax')  # 动态设置类别数
            ])

            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            # 训练模型
            model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

            # 预测
            y_pred = model.predict(X_test).argmax(axis=1)

            # 验证预测结果是否在类别范围内
            assert all(pred in range(num_classes) for pred in y_pred), "Predicted label out of range"

            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred)

            # 保存为 TensorFlow Lite 模型
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            converter.optimizations = [tf.lite.Optimize.DEFAULT]  # 启用优化（可选）
            tflite_model = converter.convert()
            tflite_model_path = os.path.join(folder_path, f"{file_name.replace('.csv', '')}_eco2_model.tflite")
            with open(tflite_model_path, "wb") as f:
                f.write(tflite_model)

            # 将结果写入 PDF
            pdf.cell(200, 10, txt=f"File: {file_name}", ln=True)
            pdf.cell(200, 10, txt=f"Accuracy: {accuracy:.4f}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Classification Report:\n{report}")
            pdf.ln(5)  # 添加间隔
            print(f"Processed {file_name}, TFLite model saved to {tflite_model_path}")

        else:
            pdf.cell(200, 10, txt=f"File: {file_name} - Skipped (missing 'label' or 'eCO2')", ln=True)

# 保存 PDF
pdf.output(output_pdf_path)
print(f"Classification results and models saved. Report: {output_pdf_path}")