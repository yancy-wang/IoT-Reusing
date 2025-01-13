import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import accuracy_score, classification_report
from fpdf import FPDF
import pandas as pd
import os

# 文件夹路径
input_folder_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/merged_files'
output_folder_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files'
output_pdf_path = '/Users/wangyangyang/Desktop/Finland/summer_job/home_kitchen/level_3/processed_files/classification_results_co_ppm.pdf'

# 创建输出文件夹
os.makedirs(output_folder_path, exist_ok=True)

# 初始化 PDF 报告
pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="Classification Results Report (TFLite Model for co_ppm)", ln=True, align='C')

# 遍历文件夹中的所有 CSV 文件
for file_name in os.listdir(input_folder_path):
    if file_name.endswith('.csv') and 'co_ppm' in file_name:  # 仅处理包含 'co_ppm' 的文件
        file_path = os.path.join(input_folder_path, file_name)

        # 加载数据
        data = pd.read_csv(file_path)

        # 确保 'eCO2' 存在
        if 'eCO2' in data.columns:
            # KMeans 聚类
            X = data[['eCO2']].dropna()  # 删除缺失值
            kmeans = KMeans(n_clusters=3, random_state=42)
            labels = kmeans.fit_predict(X)

            # 保存 eCO2 和生成的 label 到新的 CSV 文件
            output_data = pd.DataFrame({
                'eCO2': X['eCO2'],
                'label': labels
            })
            output_file_name = f"{file_name.replace('.csv', '')}_with_labels.csv"
            output_file_path = os.path.join(output_folder_path, output_file_name)
            output_data.to_csv(output_file_path, index=False)
            print(f"Processed {file_name}, saved with labels to {output_file_path}")

            # 使用 TensorFlow 构建模型
            X = output_data[['eCO2']]
            y = output_data['label']

            # 数据标准化
            scaler = StandardScaler()
            X = scaler.fit_transform(X)

            # 数据分割
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # 自动获取类别数量
            num_classes = len(y.unique())

            # 构建简单神经网络模型
            model = tf.keras.Sequential([
                tf.keras.layers.Dense(8, activation='relu', input_shape=(X_train.shape[1],)),
                tf.keras.layers.Dense(num_classes, activation='softmax')  # 动态设置类别数
            ])

            model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

            # 训练模型
            model.fit(X_train, y_train, epochs=20, batch_size=16, verbose=0)

            # 预测
            y_pred = model.predict(X_test).argmax(axis=1)
            accuracy = accuracy_score(y_test, y_pred)
            report = classification_report(y_test, y_pred)

            # 保存标准化参数
            scaler_params_path = os.path.join(output_folder_path, f"{file_name.replace('.csv', '')}_scaler_params.csv")
            scaler_params = pd.DataFrame({'mean': scaler.mean_, 'scale': scaler.scale_})
            scaler_params.to_csv(scaler_params_path, index=False)
            print(f"Scaler parameters saved to {scaler_params_path}")

            # 保存为 TensorFlow Lite 模型
            converter = tf.lite.TFLiteConverter.from_keras_model(model)
            tflite_model = converter.convert()
            tflite_model_path = os.path.join(output_folder_path, f"{file_name.replace('.csv', '')}_eco2_model.tflite")
            with open(tflite_model_path, "wb") as f:
                f.write(tflite_model)
            print(f"TFLite model saved to {tflite_model_path}")

            # 写入 PDF 报告
            pdf.cell(200, 10, txt=f"File: {file_name}", ln=True)
            pdf.cell(200, 10, txt=f"Accuracy: {accuracy:.4f}", ln=True)
            pdf.multi_cell(0, 10, txt=f"Classification Report:\n{report}")
            pdf.ln(5)  # 添加间隔

        else:
            print(f"Skipped {file_name} - missing 'eCO2'")
            pdf.cell(200, 10, txt=f"File: {file_name} - Skipped (missing 'eCO2')", ln=True)

# 保存 PDF 报告
pdf.output(output_pdf_path)
print(f"Classification results and models saved. Report: {output_pdf_path}")